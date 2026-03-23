---
name: python-django
description: |
  Django implementation patterns - models, views, serializers, managers, signals, security, and testing.
  Activate when: implementing Python Django features, working with Django models, views, URLs, or DRF APIs.
triggers: ["django", "python web", "django model", "django view", "django rest", "drf", "django rest framework"]
---

# Django Implementation Patterns

> Best practices and conventions for Django and Django REST Framework projects.

## Project Structure

```
project/
├── config/              # Project settings, URLs, WSGI/ASGI
│   ├── settings/
│   │   ├── base.py      # Shared settings
│   │   ├── dev.py       # Development overrides
│   │   └── prod.py      # Production overrides
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py
├── apps/
│   └── {app_name}/
│       ├── models.py     # Data models
│       ├── views.py      # Views or ViewSets
│       ├── serializers.py # DRF serializers
│       ├── urls.py       # App URL patterns
│       ├── admin.py      # Admin configuration
│       ├── managers.py   # Custom managers/querysets
│       ├── signals.py    # Signal handlers
│       ├── services.py   # Business logic layer
│       ├── selectors.py  # Read-only query functions
│       └── tests/
│           ├── test_models.py
│           ├── test_views.py
│           └── test_services.py
├── manage.py
└── requirements/
    ├── base.txt
    ├── dev.txt
    └── prod.txt
```

## Models

### Field Conventions

```python
class Order(models.Model):
    # Always define choices as class-level enums
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"

    # Fields: most important first, then alphabetical
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, default="")

    # Timestamps always last
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.pk} ({self.status})"
```

### Custom Managers

```python
class OrderQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=Order.Status.DRAFT)

    def for_user(self, user):
        return self.filter(user=user)

    def with_totals(self):
        return self.annotate(item_count=Count("items"), subtotal=Sum("items__price"))

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

# Usage in model: objects = OrderManager()
```

### Model Rules

- Always set `on_delete` explicitly on ForeignKey/OneToOneField
- Use `related_name` on all relationships
- Add database indexes for fields used in filters and ordering
- Use `TextChoices`/`IntegerChoices` for enum fields
- Never use `null=True` on string fields — use `blank=True, default=""`
- Define `__str__` on every model
- Keep business logic in services/selectors, not in models

## Views & ViewSets (DRF)

### ViewSet Pattern

```python
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.for_user(self.request.user).with_totals()

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

### Function-Based Views

Use for simple, one-off endpoints:

```python
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_service.cancel(order, reason=request.data.get("reason", ""))
    return Response(status=status.HTTP_204_NO_CONTENT)
```

## Serializers

```python
class OrderSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total", "item_count", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

class OrderCreateSerializer(serializers.Serializer):
    """Use plain Serializer for write operations with complex logic."""
    items = OrderItemSerializer(many=True)
    notes = serializers.CharField(required=False, default="")

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    def create(self, validated_data):
        return order_service.create_order(
            user=self.context["request"].user,
            **validated_data,
        )
```

## Services Layer

Keep business logic out of views and models:

```python
# services.py
def create_order(*, user, items, notes=""):
    """Create order with items. Raises ValidationError on failure."""
    with transaction.atomic():
        order = Order.objects.create(user=user, notes=notes)
        for item_data in items:
            OrderItem.objects.create(order=order, **item_data)
        order.total = order.items.aggregate(total=Sum("price"))["total"]
        order.save(update_fields=["total"])
    return order

def cancel_order(order, *, reason=""):
    """Cancel an order. Raises ValueError if not cancellable."""
    if order.status not in (Order.Status.DRAFT, Order.Status.PENDING):
        raise ValueError(f"Cannot cancel order in status {order.status}")
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
```

## URL Patterns

```python
# apps/orders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path("orders/<int:order_id>/cancel/", cancel_order, name="order-cancel"),
]
```

## Security Checklist

- [ ] Use `permission_classes` on all views/viewsets
- [ ] Use `get_queryset()` to scope data to current user (not `queryset = ...`)
- [ ] Use `serializer.validated_data`, never `request.data` directly
- [ ] Set `CSRF_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_HTTPONLY = True`
- [ ] Use Django's `@method_decorator(ratelimit(...))` on auth endpoints
- [ ] Never expose internal IDs in error messages
- [ ] Use `update_fields` on `save()` to prevent accidental data overwrites

## Testing

```python
class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_create_order_with_items(self):
        order = create_order(user=self.user, items=[{"product_id": 1, "price": 10}])
        assert order.total == Decimal("10.00")
        assert order.items.count() == 1

    def test_cancel_shipped_order_raises(self):
        order = OrderFactory(user=self.user, status=Order.Status.SHIPPED)
        with pytest.raises(ValueError, match="Cannot cancel"):
            cancel_order(order)

class OrderAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_list_orders_returns_only_own(self):
        OrderFactory(user=self.user)
        OrderFactory()  # another user's order
        response = self.client.get("/api/orders/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
```

## Common Anti-Patterns

| Anti-Pattern | Better Approach |
|---|---|
| Business logic in views | Move to `services.py` |
| Fat models with 500+ lines | Split into managers, services, selectors |
| `Model.objects.filter()` in views | Use custom manager methods |
| Raw SQL in views | Use ORM querysets or managers |
| `null=True` on CharField/TextField | Use `blank=True, default=""` |
| No `select_related`/`prefetch_related` | Always optimize N+1 queries |
| Catching bare `Exception` | Catch specific exceptions |
| `request.data` without serializer | Always validate through serializer |

## Quick Reference

| Aspect | Convention |
|--------|-----------|
| **Model fields** | Most important first, timestamps last |
| **Relationships** | Always set `related_name` and `on_delete` |
| **Views** | ViewSet for CRUD, `@api_view` for one-offs |
| **Serializers** | ModelSerializer for reads, plain Serializer for writes |
| **Business logic** | In `services.py`, never in views or models |
| **Queries** | In `managers.py` or `selectors.py` |
| **Tests** | Use factories (factory_boy), test services and APIs |
