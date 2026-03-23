# Go Testing Patterns Reference

## Table-Driven Tests

```go
func TestCalculateTotal(t *testing.T) {
    tests := []struct {
        name     string
        items    []OrderItem
        expected float64
        wantErr  bool
    }{
        {
            name:     "single item",
            items:    []OrderItem{{Price: 10.00, Quantity: 2}},
            expected: 20.00,
        },
        {
            name:     "multiple items",
            items:    []OrderItem{{Price: 10.00, Quantity: 1}, {Price: 5.50, Quantity: 3}},
            expected: 26.50,
        },
        {
            name:    "empty items",
            items:   []OrderItem{},
            wantErr: true,
        },
        {
            name:     "zero quantity",
            items:    []OrderItem{{Price: 10.00, Quantity: 0}},
            expected: 0.00,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := CalculateTotal(tt.items)
            if tt.wantErr {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if got != tt.expected {
                t.Errorf("got %v, want %v", got, tt.expected)
            }
        })
    }
}
```

## HTTP Handler Testing (httptest)

```go
func TestGetOrder(t *testing.T) {
    // Setup
    mockService := &MockOrderService{
        FindByIDFunc: func(ctx context.Context, id int64) (*model.Order, error) {
            if id == 1 {
                return &model.Order{ID: 1, Status: "pending", Total: 100.00}, nil
            }
            return nil, NewNotFoundError("order", id)
        },
    }
    handler := NewHandler(mockService, slog.Default())

    tests := []struct {
        name       string
        path       string
        wantStatus int
        wantBody   string
    }{
        {
            name:       "existing order",
            path:       "/api/orders/1",
            wantStatus: http.StatusOK,
            wantBody:   `"id":1`,
        },
        {
            name:       "not found",
            path:       "/api/orders/999",
            wantStatus: http.StatusNotFound,
            wantBody:   `"error"`,
        },
        {
            name:       "invalid id",
            path:       "/api/orders/abc",
            wantStatus: http.StatusBadRequest,
            wantBody:   `"error"`,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            req := httptest.NewRequest(http.MethodGet, tt.path, nil)
            rec := httptest.NewRecorder()

            handler.Routes().ServeHTTP(rec, req)

            if rec.Code != tt.wantStatus {
                t.Errorf("status = %d, want %d", rec.Code, tt.wantStatus)
            }
            if !strings.Contains(rec.Body.String(), tt.wantBody) {
                t.Errorf("body = %s, want to contain %s", rec.Body.String(), tt.wantBody)
            }
        })
    }
}
```

### Testing POST with Request Body

```go
func TestCreateOrder(t *testing.T) {
    mockService := &MockOrderService{
        CreateFunc: func(ctx context.Context, req CreateOrderRequest) (*model.Order, error) {
            return &model.Order{ID: 1, Status: "draft"}, nil
        },
    }
    handler := NewHandler(mockService, slog.Default())

    body := `{"items": [{"product_id": 1, "quantity": 2}], "notes": "rush"}`
    req := httptest.NewRequest(http.MethodPost, "/api/orders",
        strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    rec := httptest.NewRecorder()

    handler.Routes().ServeHTTP(rec, req)

    if rec.Code != http.StatusCreated {
        t.Errorf("status = %d, want %d", rec.Code, http.StatusCreated)
    }
}
```

## Mock Implementations via Interfaces

```go
// MockOrderRepository implements OrderRepository for testing
type MockOrderRepository struct {
    FindByIDFunc func(ctx context.Context, id int64) (*model.Order, error)
    CreateFunc   func(ctx context.Context, order *model.Order) error
    DeleteFunc   func(ctx context.Context, id int64) error
}

func (m *MockOrderRepository) FindByID(ctx context.Context, id int64) (*model.Order, error) {
    return m.FindByIDFunc(ctx, id)
}

func (m *MockOrderRepository) Create(ctx context.Context, order *model.Order) error {
    return m.CreateFunc(ctx, order)
}

func (m *MockOrderRepository) Delete(ctx context.Context, id int64) error {
    return m.DeleteFunc(ctx, id)
}
```

### Usage in Service Tests

```go
func TestOrderService_FindByID(t *testing.T) {
    repo := &MockOrderRepository{
        FindByIDFunc: func(ctx context.Context, id int64) (*model.Order, error) {
            return &model.Order{ID: id, Status: "pending"}, nil
        },
    }
    svc := NewOrderService(repo)

    order, err := svc.FindByID(context.Background(), 1)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if order.ID != 1 {
        t.Errorf("order.ID = %d, want 1", order.ID)
    }
}
```

## Database Testing with testcontainers-go

```go
func TestOrderRepo_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    ctx := context.Background()

    // Start PostgreSQL container
    pgContainer, err := postgres.Run(ctx, "postgres:16",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
        testcontainers.WithWaitStrategy(
            wait.ForLog("database system is ready").
                WithStartupTimeout(30*time.Second),
        ),
    )
    if err != nil {
        t.Fatalf("start container: %v", err)
    }
    defer pgContainer.Terminate(ctx)

    connStr, _ := pgContainer.ConnectionString(ctx, "sslmode=disable")
    db, err := sqlx.Connect("postgres", connStr)
    if err != nil {
        t.Fatalf("connect: %v", err)
    }
    defer db.Close()

    // Run migrations
    runMigrations(db)

    repo := NewOrderRepo(db)

    t.Run("create and find", func(t *testing.T) {
        order := &model.Order{UserID: 1, Status: "draft", Total: 50.00}
        err := repo.Create(ctx, order)
        if err != nil {
            t.Fatalf("create: %v", err)
        }
        if order.ID == 0 {
            t.Fatal("expected ID to be set")
        }

        found, err := repo.FindByID(ctx, order.ID)
        if err != nil {
            t.Fatalf("find: %v", err)
        }
        if found.Total != 50.00 {
            t.Errorf("total = %v, want 50.00", found.Total)
        }
    })
}
```

## Testing Middleware

```go
func TestAuthMiddleware(t *testing.T) {
    mockTokenService := &MockTokenService{
        ValidateFunc: func(token string) (*Claims, error) {
            if token == "valid-token" {
                return &Claims{UserID: 1}, nil
            }
            return nil, errors.New("invalid")
        },
    }

    protected := AuthMiddleware(mockTokenService)(
        http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            w.WriteHeader(http.StatusOK)
        }),
    )

    tests := []struct {
        name       string
        authHeader string
        wantStatus int
    }{
        {"valid token", "Bearer valid-token", http.StatusOK},
        {"invalid token", "Bearer bad-token", http.StatusUnauthorized},
        {"missing token", "", http.StatusUnauthorized},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            req := httptest.NewRequest("GET", "/", nil)
            if tt.authHeader != "" {
                req.Header.Set("Authorization", tt.authHeader)
            }
            rec := httptest.NewRecorder()
            protected.ServeHTTP(rec, req)

            if rec.Code != tt.wantStatus {
                t.Errorf("status = %d, want %d", rec.Code, tt.wantStatus)
            }
        })
    }
}
```

## Test Helpers

```go
// testutil/helpers.go
func AssertStatus(t *testing.T, got, want int) {
    t.Helper()
    if got != want {
        t.Errorf("status = %d, want %d", got, want)
    }
}

func AssertContains(t *testing.T, body, substr string) {
    t.Helper()
    if !strings.Contains(body, substr) {
        t.Errorf("body = %q, want to contain %q", body, substr)
    }
}

func MustParseJSON[T any](t *testing.T, body []byte) T {
    t.Helper()
    var v T
    if err := json.Unmarshal(body, &v); err != nil {
        t.Fatalf("parse JSON: %v", err)
    }
    return v
}
```

## Testing Rules

| Rule | Reason |
|---|---|
| Use table-driven tests for multiple cases | Readable, easy to extend |
| Use `t.Run` for subtests | Parallel execution, clear output |
| Use `t.Helper()` in test helpers | Correct line numbers in errors |
| Use `httptest` for HTTP tests | No real server needed |
| Mock via interfaces, not frameworks | Idiomatic Go, compile-time safety |
| Use `-short` flag for integration tests | Skip slow tests in CI |
| Use `t.Parallel()` where safe | Faster test execution |
| Never use `os.Exit` in tests | Use `t.Fatal` instead |
