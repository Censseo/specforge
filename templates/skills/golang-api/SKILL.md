---
name: golang-api
description: |
  Go API implementation patterns - interfaces, error handling, HTTP handlers, middleware, database, and testing.
  Activate when: implementing Go API features, working with Go HTTP handlers, middleware, or database operations.
triggers: ["golang", "go api", "go http", "gin", "echo", "chi", "fiber", "go server"]
---

# Go API Implementation Patterns

> Best practices and conventions for Go API development (Go 1.21+).

## Project Structure

```
cmd/
├── server/
│   └── main.go               # Entry point, wire dependencies
internal/
├── config/
│   └── config.go             # Configuration loading (env vars)
├── handler/
│   ├── handler.go            # Handler struct + constructor
│   ├── order.go              # Order HTTP handlers
│   └── middleware.go          # HTTP middleware
├── service/
│   ├── order.go              # Business logic
│   └── order_test.go
├── repository/
│   ├── order.go              # Database operations
│   └── order_test.go
├── model/
│   └── order.go              # Domain types
└── pkg/
    ├── httputil/
    │   └── response.go        # JSON response helpers
    └── validate/
        └── validate.go        # Input validation
go.mod
go.sum
```

**Rules:**
- `cmd/` for entry points only (minimal code)
- `internal/` for application code (not importable externally)
- `pkg/` for reusable utilities (importable by other projects)
- No circular dependencies between packages

## Interfaces

### Accept Interfaces, Return Structs

```go
// Define interfaces where they are USED, not where they are implemented
type OrderRepository interface {
    FindByID(ctx context.Context, id int64) (*model.Order, error)
    FindAll(ctx context.Context, filter OrderFilter) ([]model.Order, error)
    Create(ctx context.Context, order *model.Order) error
    Update(ctx context.Context, order *model.Order) error
    Delete(ctx context.Context, id int64) error
}

type OrderService struct {
    repo OrderRepository  // Accepts interface
    // ...
}

func NewOrderService(repo OrderRepository) *OrderService {  // Returns struct
    return &OrderService{repo: repo}
}
```

**Rules:**
- Define interfaces with 1-3 methods (keep them small)
- Define interfaces in the consumer package, not the provider
- Never export interfaces "just in case"
- Name single-method interfaces with `-er` suffix: `Reader`, `Writer`, `Storer`

## Error Handling

### Custom Error Types

```go
type AppError struct {
    Code    int    `json:"-"`
    Message string `json:"message"`
    Err     error  `json:"-"`
}

func (e *AppError) Error() string { return e.Message }
func (e *AppError) Unwrap() error { return e.Err }

var (
    ErrNotFound     = &AppError{Code: 404, Message: "resource not found"}
    ErrUnauthorized = &AppError{Code: 401, Message: "unauthorized"}
    ErrForbidden    = &AppError{Code: 403, Message: "forbidden"}
)

func NewNotFoundError(resource string, id any) *AppError {
    return &AppError{
        Code:    404,
        Message: fmt.Sprintf("%s with id %v not found", resource, id),
        Err:     ErrNotFound,
    }
}
```

### Error Wrapping

```go
func (r *OrderRepo) FindByID(ctx context.Context, id int64) (*model.Order, error) {
    var order model.Order
    err := r.db.QueryRowContext(ctx,
        "SELECT id, status, total FROM orders WHERE id = $1", id,
    ).Scan(&order.ID, &order.Status, &order.Total)

    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, NewNotFoundError("order", id)
        }
        return nil, fmt.Errorf("query order %d: %w", id, err)
    }
    return &order, nil
}
```

### Error Rules

- Always handle errors immediately (no `_ = err`)
- Wrap errors with context: `fmt.Errorf("doing X: %w", err)`
- Use `errors.Is` and `errors.As` for error checking
- Return errors, don't panic (except truly unrecoverable situations)
- Log errors at the top level (handler), not in services/repositories

## HTTP Handlers

### Standard Library (net/http)

```go
type Handler struct {
    orderService *service.OrderService
    logger       *slog.Logger
}

func NewHandler(os *service.OrderService, logger *slog.Logger) *Handler {
    return &Handler{orderService: os, logger: logger}
}

func (h *Handler) Routes() http.Handler {
    mux := http.NewServeMux()
    mux.HandleFunc("GET /api/orders", h.ListOrders)
    mux.HandleFunc("GET /api/orders/{id}", h.GetOrder)
    mux.HandleFunc("POST /api/orders", h.CreateOrder)
    mux.HandleFunc("DELETE /api/orders/{id}", h.DeleteOrder)
    return mux
}

func (h *Handler) GetOrder(w http.ResponseWriter, r *http.Request) {
    id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
    if err != nil {
        httputil.Error(w, http.StatusBadRequest, "invalid order id")
        return
    }

    order, err := h.orderService.FindByID(r.Context(), id)
    if err != nil {
        var appErr *AppError
        if errors.As(err, &appErr) {
            httputil.Error(w, appErr.Code, appErr.Message)
            return
        }
        h.logger.Error("get order", "error", err, "id", id)
        httputil.Error(w, http.StatusInternalServerError, "internal error")
        return
    }

    httputil.JSON(w, http.StatusOK, order)
}
```

### JSON Response Helpers

```go
// pkg/httputil/response.go
func JSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(map[string]any{
        "status": "success",
        "data":   data,
    })
}

func Error(w http.ResponseWriter, status int, message string) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(map[string]any{
        "status": "error",
        "error":  message,
    })
}
```

## Middleware

```go
func LoggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            ww := &responseWriter{ResponseWriter: w, status: http.StatusOK}

            next.ServeHTTP(ww, r)

            logger.Info("request",
                "method", r.Method,
                "path", r.URL.Path,
                "status", ww.status,
                "duration", time.Since(start),
            )
        })
    }
}

func AuthMiddleware(tokenService TokenService) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            token := r.Header.Get("Authorization")
            if token == "" {
                httputil.Error(w, http.StatusUnauthorized, "missing token")
                return
            }

            claims, err := tokenService.Validate(strings.TrimPrefix(token, "Bearer "))
            if err != nil {
                httputil.Error(w, http.StatusUnauthorized, "invalid token")
                return
            }

            ctx := context.WithValue(r.Context(), userContextKey, claims)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

// Chain middleware
handler := LoggingMiddleware(logger)(
    AuthMiddleware(tokenService)(
        h.Routes(),
    ),
)
```

## Database (sqlx/pgx)

```go
type OrderRepo struct {
    db *sqlx.DB
}

func NewOrderRepo(db *sqlx.DB) *OrderRepo {
    return &OrderRepo{db: db}
}

func (r *OrderRepo) FindAll(ctx context.Context, filter OrderFilter) ([]model.Order, error) {
    query := "SELECT id, user_id, status, total, created_at FROM orders WHERE 1=1"
    args := []any{}
    argIdx := 1

    if filter.Status != "" {
        query += fmt.Sprintf(" AND status = $%d", argIdx)
        args = append(args, filter.Status)
        argIdx++
    }
    if filter.UserID > 0 {
        query += fmt.Sprintf(" AND user_id = $%d", argIdx)
        args = append(args, filter.UserID)
        argIdx++
    }

    query += " ORDER BY created_at DESC LIMIT $" + strconv.Itoa(argIdx)
    args = append(args, filter.Limit)

    var orders []model.Order
    if err := r.db.SelectContext(ctx, &orders, query, args...); err != nil {
        return nil, fmt.Errorf("query orders: %w", err)
    }
    return orders, nil
}

// Transactions
func (r *OrderRepo) CreateWithItems(ctx context.Context, order *model.Order, items []model.OrderItem) error {
    tx, err := r.db.BeginTxx(ctx, nil)
    if err != nil {
        return fmt.Errorf("begin tx: %w", err)
    }
    defer tx.Rollback()

    err = tx.QueryRowxContext(ctx,
        "INSERT INTO orders (user_id, status, total) VALUES ($1, $2, $3) RETURNING id",
        order.UserID, order.Status, order.Total,
    ).Scan(&order.ID)
    if err != nil {
        return fmt.Errorf("insert order: %w", err)
    }

    for i := range items {
        items[i].OrderID = order.ID
        _, err = tx.ExecContext(ctx,
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
            items[i].OrderID, items[i].ProductID, items[i].Quantity, items[i].Price,
        )
        if err != nil {
            return fmt.Errorf("insert item: %w", err)
        }
    }

    return tx.Commit()
}
```

## Context Usage

```go
// Pass context through the entire call chain
func (s *OrderService) FindByID(ctx context.Context, id int64) (*model.Order, error) {
    return s.repo.FindByID(ctx, id)
}

// Context with timeout
ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
defer cancel()
order, err := s.orderService.FindByID(ctx, id)
```

## Input Validation

```go
type CreateOrderRequest struct {
    Items []OrderItemRequest `json:"items" validate:"required,min=1,dive"`
    Notes string             `json:"notes" validate:"max=500"`
}

type OrderItemRequest struct {
    ProductID int64 `json:"product_id" validate:"required,gt=0"`
    Quantity  int   `json:"quantity" validate:"required,min=1,max=100"`
}

// Decode and validate
func decodeAndValidate[T any](r *http.Request) (T, error) {
    var req T
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        return req, fmt.Errorf("decode: %w", err)
    }
    if err := validate.Struct(req); err != nil {
        return req, fmt.Errorf("validate: %w", err)
    }
    return req, nil
}
```

## Security Checklist

- [ ] Use parameterized queries (`$1`, `$2`), never string concatenation
- [ ] Validate all input (path params, query params, request body)
- [ ] Use context timeouts on all I/O operations
- [ ] Use `crypto/rand` for tokens, never `math/rand`
- [ ] Set rate limiting middleware on public endpoints
- [ ] Never log sensitive data (passwords, tokens, PII)
- [ ] Use `httpOnly`, `Secure`, `SameSite` on cookies
- [ ] Set security headers (CORS, CSP, HSTS)

## Common Anti-Patterns

| Anti-Pattern | Better Approach |
|---|---|
| Large interfaces (10+ methods) | Small interfaces (1-3 methods) |
| Defining interfaces in provider package | Define interfaces where consumed |
| Ignoring errors (`_ = err`) | Always handle: return, log, or wrap |
| Panicking in library code | Return errors |
| Global variables for DB/config | Dependency injection via constructors |
| Using `context.Value` for required data | Pass as function parameters |
| Goroutine leak (no cancellation) | Use `context.WithCancel` or `context.WithTimeout` |
| `init()` functions for setup | Explicit initialization in `main()` |

## Quick Reference

| Aspect | Convention |
|--------|-----------|
| **Structure** | `cmd/` + `internal/` + `pkg/` |
| **Interfaces** | Small, defined at consumer |
| **Errors** | Wrap with `%w`, check with `errors.Is/As` |
| **Handlers** | Method on struct, inject dependencies |
| **Middleware** | `func(http.Handler) http.Handler` |
| **Database** | sqlx/pgx, parameterized queries, transactions |
| **Context** | Pass through entire chain, use timeouts |
| **Validation** | Struct tags + validator library |
| **Testing** | Table-driven, httptest, interfaces for mocking |
| **Logging** | `slog` (structured), log at handler level |
