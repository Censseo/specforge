# Spring Boot Testing Patterns Reference

## Test Annotations

| Annotation | Scope | Context | Speed |
|---|---|---|---|
| `@SpringBootTest` | Full application | All beans | Slow |
| `@WebMvcTest` | Controller layer | Web + MockMvc | Fast |
| `@DataJpaTest` | Repository layer | JPA + H2/TC | Fast |
| `@JsonTest` | JSON serialization | Jackson | Fast |
| Unit test (no annotation) | Single class | None | Fastest |

## Controller Tests (@WebMvcTest)

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private OrderService orderService;

    @Test
    void list_returns_paginated_orders() throws Exception {
        Page<OrderDto> page = new PageImpl<>(List.of(
            new OrderDto(1L, "PENDING", BigDecimal.TEN)
        ));
        when(orderService.findAll(any(Pageable.class))).thenReturn(page);

        mockMvc.perform(get("/api/v1/orders")
                .param("page", "0")
                .param("size", "20"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.content[0].id").value(1))
            .andExpect(jsonPath("$.data.content[0].status").value("PENDING"));
    }

    @Test
    void create_with_valid_input_returns_201() throws Exception {
        OrderDto created = new OrderDto(1L, "DRAFT", BigDecimal.TEN);
        when(orderService.create(any())).thenReturn(created);

        mockMvc.perform(post("/api/v1/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"items": [{"productId": 1, "quantity": 2}], "notes": "Rush"}
                    """))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"))
            .andExpect(jsonPath("$.data.id").value(1));
    }

    @Test
    void create_with_invalid_input_returns_400() throws Exception {
        mockMvc.perform(post("/api/v1/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"items": [], "notes": ""}
                    """))
            .andExpect(status().isBadRequest());
    }

    @Test
    void get_nonexistent_returns_404() throws Exception {
        when(orderService.findById(999L))
            .thenThrow(new ResourceNotFoundException("Order", 999L));

        mockMvc.perform(get("/api/v1/orders/999"))
            .andExpect(status().isNotFound());
    }
}
```

### Testing with Security

```java
@WebMvcTest(OrderController.class)
@Import(SecurityConfig.class)
class OrderControllerSecurityTest {
    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private OrderService orderService;

    @Test
    void unauthenticated_request_returns_401() throws Exception {
        mockMvc.perform(get("/api/v1/orders"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(roles = "USER")
    void authenticated_user_can_list_orders() throws Exception {
        when(orderService.findAll(any())).thenReturn(Page.empty());
        mockMvc.perform(get("/api/v1/orders"))
            .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "USER")
    void non_admin_cannot_access_admin_endpoint() throws Exception {
        mockMvc.perform(get("/api/v1/admin/orders"))
            .andExpect(status().isForbidden());
    }
}
```

## Repository Tests (@DataJpaTest)

```java
@DataJpaTest
class OrderRepositoryTest {
    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private TestEntityManager em;

    @Test
    void findByStatusWithItems_fetches_items_eagerly() {
        Order order = new Order();
        order.setStatus(OrderStatus.PENDING);
        order.addItem(new OrderItem(null, "Product A", BigDecimal.TEN));
        em.persistAndFlush(order);
        em.clear(); // Force fresh load

        List<Order> found = orderRepository.findByStatusWithItems(OrderStatus.PENDING);

        assertThat(found).hasSize(1);
        assertThat(found.get(0).getItems()).hasSize(1); // No LazyInitializationException
    }

    @Test
    void findByUserIdAndStatus_returns_matching_orders() {
        User user = em.persist(new User("test@example.com"));
        Order o1 = em.persist(createOrder(user, OrderStatus.PENDING));
        Order o2 = em.persist(createOrder(user, OrderStatus.SHIPPED));
        em.flush();

        Page<Order> result = orderRepository.findByUserIdAndStatus(
            user.getId(), OrderStatus.PENDING, Pageable.unpaged());

        assertThat(result.getContent()).containsExactly(o1);
    }
}
```

## Integration Tests (@SpringBootTest)

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("testdb");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void full_order_lifecycle() {
        // Create
        var createRequest = new CreateOrderRequest(
            List.of(new OrderItemRequest(1L, 2)), "Test order"
        );
        var createResponse = restTemplate.postForEntity(
            "/api/v1/orders", createRequest, ApiResponse.class);
        assertThat(createResponse.getStatusCode()).isEqualTo(HttpStatus.CREATED);

        // Read
        Long orderId = extractId(createResponse.getBody());
        var getResponse = restTemplate.getForEntity(
            "/api/v1/orders/" + orderId, ApiResponse.class);
        assertThat(getResponse.getStatusCode()).isEqualTo(HttpStatus.OK);

        // Delete
        restTemplate.delete("/api/v1/orders/" + orderId);
        var afterDelete = restTemplate.getForEntity(
            "/api/v1/orders/" + orderId, ApiResponse.class);
        assertThat(afterDelete.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
```

## Service Layer Unit Tests

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock
    private OrderRepository orderRepository;

    @Mock
    private OrderMapper orderMapper;

    @InjectMocks
    private OrderService orderService;

    @Test
    void findById_returns_dto() {
        Order order = new Order();
        order.setId(1L);
        OrderDto dto = new OrderDto(1L, "DRAFT", BigDecimal.TEN);

        when(orderRepository.findByIdWithItems(1L)).thenReturn(Optional.of(order));
        when(orderMapper.toDto(order)).thenReturn(dto);

        OrderDto result = orderService.findById(1L);

        assertThat(result.id()).isEqualTo(1L);
        verify(orderRepository).findByIdWithItems(1L);
    }

    @Test
    void findById_throws_when_not_found() {
        when(orderRepository.findByIdWithItems(999L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> orderService.findById(999L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("Order");
    }
}
```

## Test Configuration

### Test Profiles

```yaml
# src/test/resources/application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
```

### Shared Test Utilities

```java
public class TestFixtures {
    public static Order createOrder(User user, OrderStatus status) {
        Order order = new Order();
        order.setUser(user);
        order.setStatus(status);
        order.setTotal(BigDecimal.valueOf(100));
        return order;
    }
}
```

## Testing Rules

| Rule | Reason |
|---|---|
| Use `@WebMvcTest` for controller tests | Faster than full context |
| Use `@DataJpaTest` for repository tests | Auto-configures JPA + in-memory DB |
| Use Testcontainers for integration tests | Real database behavior |
| Mock service layer in controller tests | Isolate HTTP layer |
| Use `@MockitoBean` (not `@Mock`) in Spring tests | Integrates with Spring context |
| Clear EntityManager before assertions | Verify DB state, not cache |
| Test validation constraints in controller tests | `@Valid` is a web-layer concern |
| Test transactional behavior with `TransactionTemplate` | Verify rollback on errors |
