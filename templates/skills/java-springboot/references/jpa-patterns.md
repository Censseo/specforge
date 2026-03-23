# Spring Boot JPA Patterns Reference

## Entity Relationships

### One-to-Many (Parent owns children)

```java
// Parent
@Entity
public class Order {
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }

    public void removeItem(OrderItem item) {
        items.remove(item);
        item.setOrder(null);
    }
}

// Child
@Entity
public class OrderItem {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;
}
```

### Many-to-Many

```java
@Entity
public class Student {
    @ManyToMany
    @JoinTable(
        name = "student_course",
        joinColumns = @JoinColumn(name = "student_id"),
        inverseJoinColumns = @JoinColumn(name = "course_id")
    )
    private Set<Course> courses = new HashSet<>();
}
```

For extra attributes on the join table, use an explicit entity with `@EmbeddedId`.

### One-to-One

```java
@Entity
public class User {
    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private UserProfile profile;
}

@Entity
public class UserProfile {
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @MapsId
    private User user;
}
```

## N+1 Prevention

### Problem

```java
// BAD: N+1 queries (1 for orders + N for each order's items)
List<Order> orders = orderRepository.findAll();
orders.forEach(o -> o.getItems().size()); // Triggers N queries
```

### Solutions

```java
// Solution 1: JOIN FETCH in JPQL
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.status = :status")
List<Order> findByStatusWithItems(@Param("status") OrderStatus status);

// Solution 2: @EntityGraph
@EntityGraph(attributePaths = {"items", "items.product"})
List<Order> findByStatus(OrderStatus status);

// Solution 3: Batch fetching (in application.properties)
// spring.jpa.properties.hibernate.default_batch_fetch_size=20
```

## Specifications (Dynamic Queries)

```java
public class OrderSpecs {
    public static Specification<Order> hasStatus(OrderStatus status) {
        return (root, query, cb) -> cb.equal(root.get("status"), status);
    }

    public static Specification<Order> createdAfter(LocalDateTime date) {
        return (root, query, cb) -> cb.greaterThan(root.get("createdAt"), date);
    }

    public static Specification<Order> totalGreaterThan(BigDecimal amount) {
        return (root, query, cb) -> cb.greaterThan(root.get("total"), amount);
    }
}

// Usage in service
public Page<Order> search(OrderStatus status, BigDecimal minTotal, Pageable pageable) {
    Specification<Order> spec = Specification.where(null);
    if (status != null) spec = spec.and(OrderSpecs.hasStatus(status));
    if (minTotal != null) spec = spec.and(OrderSpecs.totalGreaterThan(minTotal));
    return orderRepository.findAll(spec, pageable);
}

// Repository must extend JpaSpecificationExecutor
public interface OrderRepository extends JpaRepository<Order, Long>,
        JpaSpecificationExecutor<Order> {}
```

## Pagination and Sorting

### Controller

```java
@GetMapping
public ResponseEntity<Page<OrderDto>> list(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size,
        @RequestParam(defaultValue = "createdAt") String sortBy,
        @RequestParam(defaultValue = "desc") String direction) {

    Sort sort = Sort.by(Sort.Direction.fromString(direction), sortBy);
    Pageable pageable = PageRequest.of(page, Math.min(size, 100), sort);
    return ResponseEntity.ok(orderService.findAll(pageable));
}
```

### Cursor-Based Pagination

```java
@Query("SELECT o FROM Order o WHERE o.createdAt < :cursor ORDER BY o.createdAt DESC")
List<Order> findBeforeCursor(@Param("cursor") LocalDateTime cursor, Pageable pageable);
```

## Auditing

```java
@Configuration
@EnableJpaAuditing
public class JpaConfig {}

@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(updatable = false)
    private String createdBy;

    @LastModifiedBy
    private String updatedBy;
}

// AuditorAware implementation
@Component
public class SecurityAuditorAware implements AuditorAware<String> {
    @Override
    public Optional<String> getCurrentAuditor() {
        return Optional.ofNullable(SecurityContextHolder.getContext().getAuthentication())
            .map(Authentication::getName);
    }
}
```

## Soft Delete

```java
@Entity
@SQLDelete(sql = "UPDATE orders SET deleted_at = NOW() WHERE id = ?")
@SQLRestriction("deleted_at IS NULL")
public class Order extends BaseEntity {
    private LocalDateTime deletedAt;
}
```

## Projections (DTOs from Queries)

### Interface Projection

```java
public interface OrderSummary {
    Long getId();
    String getStatus();
    BigDecimal getTotal();
    LocalDateTime getCreatedAt();
}

// In repository
List<OrderSummary> findByUserId(Long userId);
```

### Constructor Expression

```java
@Query("SELECT new com.example.dto.OrderStats(o.status, COUNT(o), SUM(o.total)) " +
       "FROM Order o GROUP BY o.status")
List<OrderStats> getOrderStats();
```

## JPA Rules

| Rule | Reason |
|---|---|
| Always `FetchType.LAZY` | Prevent unintended eager loading |
| Use `JOIN FETCH` or `@EntityGraph` | Explicit eager loading when needed |
| Set `batch_fetch_size` | Mitigate N+1 for batch scenarios |
| Use Specifications for dynamic filters | Composable, type-safe queries |
| Cap page size in controller | Prevent `size=999999` |
| Use `@Version` for optimistic locking | Prevent lost updates |
| Use projections for read-only queries | Reduce memory and serialization overhead |
| Index foreign keys and filter columns | Query performance |
