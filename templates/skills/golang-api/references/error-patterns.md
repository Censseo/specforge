# Go Error Patterns Reference

## Error Wrapping and Unwrapping

### Wrapping with Context

```go
// Add context at each layer
func (r *OrderRepo) FindByID(ctx context.Context, id int64) (*Order, error) {
    var order Order
    err := r.db.GetContext(ctx, &order, "SELECT * FROM orders WHERE id = $1", id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, fmt.Errorf("find order %d: %w", id, ErrNotFound)
        }
        return nil, fmt.Errorf("find order %d: %w", id, err)
    }
    return &order, nil
}

func (s *OrderService) GetOrder(ctx context.Context, id int64) (*OrderDTO, error) {
    order, err := s.repo.FindByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get order: %w", err)
    }
    return toDTO(order), nil
}
```

Error chain: `get order: find order 42: not found`

### Unwrapping

```go
// errors.Is — checks the error chain for a match
if errors.Is(err, ErrNotFound) {
    // Handle not found
}

// errors.As — extracts a specific error type
var appErr *AppError
if errors.As(err, &appErr) {
    httputil.Error(w, appErr.Code, appErr.Message)
    return
}
```

## Sentinel Errors vs Custom Types

### Sentinel Errors (Simple)

Use for well-known, fixed error conditions:

```go
var (
    ErrNotFound      = errors.New("not found")
    ErrAlreadyExists = errors.New("already exists")
    ErrInvalidInput  = errors.New("invalid input")
    ErrUnauthorized  = errors.New("unauthorized")
    ErrForbidden     = errors.New("forbidden")
)
```

### Custom Error Types (Rich Context)

Use when errors need structured data:

```go
type ValidationError struct {
    Field   string `json:"field"`
    Message string `json:"message"`
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation: %s: %s", e.Field, e.Message)
}

type ValidationErrors struct {
    Errors []ValidationError `json:"errors"`
}

func (e *ValidationErrors) Error() string {
    return fmt.Sprintf("%d validation errors", len(e.Errors))
}

// Usage
func validateOrder(req CreateOrderRequest) error {
    var errs []ValidationError
    if len(req.Items) == 0 {
        errs = append(errs, ValidationError{Field: "items", Message: "required"})
    }
    if req.Notes != "" && len(req.Notes) > 500 {
        errs = append(errs, ValidationError{Field: "notes", Message: "max 500 chars"})
    }
    if len(errs) > 0 {
        return &ValidationErrors{Errors: errs}
    }
    return nil
}
```

### AppError (HTTP-Aware)

```go
type AppError struct {
    Code    int    `json:"-"`
    Message string `json:"message"`
    Detail  string `json:"detail,omitempty"`
    Err     error  `json:"-"`
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %v", e.Message, e.Err)
    }
    return e.Message
}

func (e *AppError) Unwrap() error { return e.Err }

// Constructors
func ErrBadRequest(message string) *AppError {
    return &AppError{Code: 400, Message: message}
}

func ErrNotFoundf(resource string, id any) *AppError {
    return &AppError{
        Code:    404,
        Message: fmt.Sprintf("%s %v not found", resource, id),
        Err:     ErrNotFound,
    }
}

func ErrInternalf(format string, args ...any) *AppError {
    return &AppError{
        Code:    500,
        Message: "internal server error",
        Detail:  fmt.Sprintf(format, args...),
    }
}
```

## Error Handling in HTTP Handlers

### Centralized Error Handler

```go
// HandlerFunc that returns an error
type AppHandler func(w http.ResponseWriter, r *http.Request) error

// Adapter converts AppHandler to http.HandlerFunc
func HandleError(h AppHandler) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        err := h(w, r)
        if err == nil {
            return
        }

        // Check for AppError
        var appErr *AppError
        if errors.As(err, &appErr) {
            httputil.Error(w, appErr.Code, appErr.Message)
            return
        }

        // Check for validation errors
        var valErrs *ValidationErrors
        if errors.As(err, &valErrs) {
            httputil.JSON(w, http.StatusBadRequest, valErrs)
            return
        }

        // Default: internal server error
        slog.Error("unhandled error", "error", err)
        httputil.Error(w, http.StatusInternalServerError, "internal error")
    }
}

// Usage
mux.HandleFunc("GET /api/orders/{id}", HandleError(h.GetOrder))

func (h *Handler) GetOrder(w http.ResponseWriter, r *http.Request) error {
    id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
    if err != nil {
        return ErrBadRequest("invalid order id")
    }

    order, err := h.service.FindByID(r.Context(), id)
    if err != nil {
        return err // AppError propagates with correct status code
    }

    httputil.JSON(w, http.StatusOK, order)
    return nil
}
```

## Structured Error Responses

### JSON Error Format

```json
{
    "status": "error",
    "error": {
        "code": "NOT_FOUND",
        "message": "order 42 not found"
    }
}
```

```json
{
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "2 validation errors",
        "details": [
            {"field": "items", "message": "required"},
            {"field": "quantity", "message": "must be > 0"}
        ]
    }
}
```

## Error Rules

| Rule | Reason |
|---|---|
| Always wrap with context: `fmt.Errorf("doing X: %w", err)` | Traceable error chains |
| Use sentinel errors for fixed conditions | Simple, comparable |
| Use custom types for structured errors | Rich context for handlers |
| Handle errors at the handler level | Single place for HTTP mapping |
| Never ignore errors (no `_ = err`) | Silent failures are bugs |
| Log unexpected errors, return expected ones | Don't log validation errors |
| Use `%w` verb, not `%v`, for wrapping | Preserves error chain |
| Don't wrap errors with the same message | Avoid redundancy in chain |
