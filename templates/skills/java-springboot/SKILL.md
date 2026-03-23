---
name: java-springboot
description: |
  Spring Boot implementation patterns - dependency injection, REST controllers, JPA, security, and testing.
  Activate when: implementing Java Spring Boot features, working with Spring DI, JPA, or Spring Security.
triggers: ["spring boot", "spring", "java api", "jpa", "spring security", "spring data"]
---

# Spring Boot Implementation Patterns

> Best practices and conventions for Spring Boot 3+ with Java 17+.

## Project Structure

```
src/main/java/com/example/app/
├── config/                    # @Configuration classes
│   ├── SecurityConfig.java
│   └── WebConfig.java
├── feature/                   # Package-by-feature (not by layer)
│   └── order/
│       ├── Order.java         # Entity
│       ├── OrderRepository.java
│       ├── OrderService.java
│       ├── OrderController.java
│       ├── OrderDto.java
│       ├── CreateOrderRequest.java
│       └── OrderMapper.java
├── common/
│   ├── exception/             # Global exception handling
│   │   ├── GlobalExceptionHandler.java
│   │   └── ResourceNotFoundException.java
│   └── dto/
│       └── ApiResponse.java
└── Application.java

src/test/java/com/example/app/
├── feature/order/
│   ├── OrderControllerTest.java   # @WebMvcTest
│   ├── OrderRepositoryTest.java   # @DataJpaTest
│   ├── OrderServiceTest.java      # Unit test
│   └── OrderIntegrationTest.java  # @SpringBootTest
```

**Package by feature, not by layer.** Keep Order entity, repository, service, and controller in the same package.

## Dependency Injection

### Constructor Injection (Preferred)

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
    private final EventPublisher eventPublisher;

    // Single constructor — @Autowired is optional
    public OrderService(
            OrderRepository orderRepository,
            PaymentService paymentService,
            EventPublisher eventPublisher) {
        this.orderRepository = orderRepository;
        this.paymentService = paymentService;
        this.eventPublisher = eventPublisher;
    }
}
```

**Rules:**
- Always use constructor injection (never `@Autowired` on fields)
- Mark dependencies as `final`
- If constructor has too many params (>5), the class has too many responsibilities

### Configuration

```java
@Configuration
public class AppConfig {
    @Bean
    @ConditionalOnProperty(name = "app.notifications.enabled", havingValue = "true")
    public NotificationService notificationService(EmailClient emailClient) {
        return new NotificationService(emailClient);
    }
}
```

## REST Controllers

### Standard Controller

```java
@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
public class OrderController {
    private final OrderService orderService;

    @GetMapping
    public ResponseEntity<ApiResponse<Page<OrderDto>>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<OrderDto> orders = orderService.findAll(PageRequest.of(page, size));
        return ResponseEntity.ok(ApiResponse.success(orders));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<OrderDto>> get(@PathVariable Long id) {
        OrderDto order = orderService.findById(id);
        return ResponseEntity.ok(ApiResponse.success(order));
    }

    @PostMapping
    public ResponseEntity<ApiResponse<OrderDto>> create(
            @Valid @RequestBody CreateOrderRequest request) {
        OrderDto created = orderService.create(request);
        URI location = URI.create("/api/v1/orders/" + created.id());
        return ResponseEntity.created(location).body(ApiResponse.success(created));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<OrderDto>> update(
            @PathVariable Long id,
            @Valid @RequestBody UpdateOrderRequest request) {
        OrderDto updated = orderService.update(id, request);
        return ResponseEntity.ok(ApiResponse.success(updated));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        orderService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

### Input Validation

```java
public record CreateOrderRequest(
    @NotNull @Size(min = 1) List<OrderItemRequest> items,
    @Size(max = 500) String notes
) {}

public record OrderItemRequest(
    @NotNull Long productId,
    @Min(1) @Max(100) int quantity
) {}
```

### API Response Wrapper

```java
public record ApiResponse<T>(
    String status,
    T data,
    String error
) {
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>("success", data, null);
    }

    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>("error", null, message);
    }
}
```

## JPA Entities

```java
@Entity
@Table(name = "orders", indexes = {
    @Index(name = "idx_order_user", columnList = "user_id"),
    @Index(name = "idx_order_status", columnList = "status")
})
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private OrderStatus status = OrderStatus.DRAFT;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal total;

    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    // Business methods
    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }
}
```

### Entity Rules

- Always use `FetchType.LAZY` on `@ManyToOne` and `@OneToMany`
- Use `@Enumerated(EnumType.STRING)`, never `EnumType.ORDINAL`
- Use `CascadeType.ALL` + `orphanRemoval = true` for owned collections
- Add `@Index` on columns used in WHERE/ORDER BY clauses
- Use `@CreatedDate` / `@LastModifiedDate` with `@EnableJpaAuditing`

## Repository

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    // Derived queries
    Page<Order> findByUserIdAndStatus(Long userId, OrderStatus status, Pageable pageable);

    // JPQL for complex queries
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
    Optional<Order> findByIdWithItems(@Param("id") Long id);

    // Native query when needed
    @Query(value = "SELECT COUNT(*) FROM orders WHERE status = :status", nativeQuery = true)
    long countByStatus(@Param("status") String status);
}
```

## Service Layer

```java
@Service
@Transactional(readOnly = true)
public class OrderService {
    private final OrderRepository orderRepository;
    private final OrderMapper orderMapper;

    @Transactional
    public OrderDto create(CreateOrderRequest request) {
        Order order = orderMapper.toEntity(request);
        order.setTotal(calculateTotal(order.getItems()));
        Order saved = orderRepository.save(order);
        return orderMapper.toDto(saved);
    }

    public OrderDto findById(Long id) {
        Order order = orderRepository.findByIdWithItems(id)
            .orElseThrow(() -> new ResourceNotFoundException("Order", id));
        return orderMapper.toDto(order);
    }

    public Page<OrderDto> findAll(Pageable pageable) {
        return orderRepository.findAll(pageable).map(orderMapper::toDto);
    }
}
```

**Rules:**
- `@Transactional(readOnly = true)` on class, `@Transactional` on write methods
- Throw specific exceptions, not generic ones
- Return DTOs, not entities

## Exception Handling

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(ApiResponse.error(ex.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Map<String, String>>> handleValidation(
            MethodArgumentNotValidException ex) {
        Map<String, String> errors = ex.getBindingResult().getFieldErrors().stream()
            .collect(Collectors.toMap(
                FieldError::getField,
                e -> e.getDefaultMessage() != null ? e.getDefaultMessage() : "Invalid"
            ));
        return ResponseEntity.badRequest().body(ApiResponse.error("Validation failed"));
    }
}
```

## Security Configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable()) // Disable for stateless APIs
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/auth/**").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }
}
```

## Security Checklist

- [ ] Use `@Valid` on all `@RequestBody` parameters
- [ ] Never expose entity IDs in error messages
- [ ] Use `@PreAuthorize` for method-level authorization
- [ ] Hash passwords with BCrypt (`PasswordEncoder`)
- [ ] Set `@Transactional` on all write operations
- [ ] Use parameterized queries (JPQL or Spring Data), never string concatenation
- [ ] Configure CORS explicitly, never use `@CrossOrigin("*")` in production
- [ ] Validate path variables and query parameters

## Common Anti-Patterns

| Anti-Pattern | Better Approach |
|---|---|
| `@Autowired` on fields | Constructor injection with `final` fields |
| Returning entities from controllers | Return DTOs via mapper |
| `FetchType.EAGER` on relationships | Always `LAZY`, use `JOIN FETCH` when needed |
| Business logic in controllers | Move to service layer |
| Generic `Exception` in throws | Specific exceptions with `@ExceptionHandler` |
| Package by layer (controllers/, services/) | Package by feature (order/, user/) |
| `@Transactional` on every method | Class-level `readOnly = true`, method-level for writes |
| Missing pagination on list endpoints | Always use `Pageable` and return `Page<>` |

## Quick Reference

| Aspect | Convention |
|--------|-----------|
| **Structure** | Package by feature |
| **DI** | Constructor injection, `final` fields |
| **Controllers** | Return `ResponseEntity<ApiResponse<T>>` |
| **Validation** | Jakarta `@Valid` + record constraints |
| **Entities** | `LAZY` fetch, `STRING` enums, audit fields |
| **Repositories** | Derived queries or `@Query` JPQL |
| **Services** | `readOnly = true` class-level, DTOs out |
| **Errors** | `@RestControllerAdvice` + custom exceptions |
| **Testing** | `@WebMvcTest`, `@DataJpaTest`, `@SpringBootTest` |
