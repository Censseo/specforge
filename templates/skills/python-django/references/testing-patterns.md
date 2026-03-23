# Django Testing Patterns Reference

## Factory-Based Test Data (factory_boy)

### Basic Factory

```python
import factory
from apps.users.models import User
from apps.orders.models import Order

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    status = Order.Status.DRAFT
    total = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
```

### Factory Traits

```python
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    class Params:
        admin = factory.Trait(
            is_staff=True,
            is_superuser=True,
        )
        inactive = factory.Trait(
            is_active=False,
        )

# Usage: UserFactory(admin=True), UserFactory(inactive=True)
```

### Related Objects

```python
class OrderWithItemsFactory(OrderFactory):
    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for item in extracted:
                self.items.add(item)
        else:
            OrderItemFactory.create_batch(3, order=self)
```

## API Test Patterns (DRF)

### ViewSet Tests

```python
from rest_framework.test import APITestCase
from rest_framework import status

class OrderAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
        self.url = "/api/orders/"

    def test_list_returns_own_orders_only(self):
        OrderFactory(user=self.user)
        OrderFactory()  # another user
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_create_order(self):
        data = {"items": [{"product_id": 1, "quantity": 2}], "notes": "Rush"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.filter(user=self.user).exists()

    def test_create_order_unauthenticated(self):
        self.client.force_authenticate(None)
        response = self.client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_access_other_users_order(self):
        other_order = OrderFactory()
        response = self.client.get(f"{self.url}{other_order.pk}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
```

### Pagination Tests

```python
def test_list_is_paginated(self):
    OrderFactory.create_batch(25, user=self.user)
    response = self.client.get(self.url)
    assert response.status_code == 200
    assert "next" in response.data
    assert len(response.data["results"]) == 20  # default page size
```

### File Upload Tests

```python
from django.core.files.uploadedfile import SimpleUploadedFile

def test_upload_avatar(self):
    image = SimpleUploadedFile("avatar.png", b"fake-image-content", content_type="image/png")
    response = self.client.patch(f"/api/users/{self.user.pk}/", {"avatar": image}, format="multipart")
    assert response.status_code == 200
```

## Service Layer Tests

```python
from django.test import TestCase

class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_create_order_calculates_total(self):
        order = create_order(
            user=self.user,
            items=[
                {"product_id": 1, "price": Decimal("10.00")},
                {"product_id": 2, "price": Decimal("25.00")},
            ],
        )
        assert order.total == Decimal("35.00")

    def test_create_order_atomic(self):
        """If item creation fails, order should not be created."""
        with pytest.raises(ValidationError):
            create_order(user=self.user, items=[{"product_id": None, "price": -1}])
        assert Order.objects.count() == 0

    def test_cancel_order_updates_status(self):
        order = OrderFactory(user=self.user, status=Order.Status.PENDING)
        cancel_order(order, reason="Changed mind")
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED
```

## Mocking External Services

```python
from unittest.mock import patch, MagicMock

class PaymentServiceTest(TestCase):
    @patch("apps.payments.services.stripe.Charge.create")
    def test_process_payment(self, mock_charge):
        mock_charge.return_value = MagicMock(id="ch_123", status="succeeded")
        result = process_payment(order=OrderFactory(), token="tok_visa")
        assert result.stripe_charge_id == "ch_123"
        mock_charge.assert_called_once()

    @patch("apps.notifications.services.send_email")
    def test_order_confirmation_sends_email(self, mock_email):
        order = OrderFactory(status=Order.Status.CONFIRMED)
        send_order_confirmation(order)
        mock_email.assert_called_once_with(
            to=order.user.email,
            template="order_confirmed",
            context={"order": order},
        )
```

## Database Transaction Isolation

```python
from django.test import TransactionTestCase

class ConcurrencyTest(TransactionTestCase):
    """Use TransactionTestCase when testing transaction behavior."""

    def test_concurrent_stock_update(self):
        product = ProductFactory(stock=1)
        # Simulate concurrent purchase
        with self.assertRaises(InsufficientStockError):
            with transaction.atomic():
                purchase_product(product, quantity=1)
                purchase_product(product, quantity=1)
```

## Fixture-Free Testing Rules

| Practice | Reason |
|---|---|
| Use factories, not fixtures | Factories are explicit, composable, and type-safe |
| Create data in `setUp` or test method | Keep tests self-contained |
| Use `create_batch` for bulk data | Cleaner than loops |
| Use traits for variations | Avoid factory explosion |
| Never share mutable state between tests | Each test is independent |
| Use `refresh_from_db()` after mutations | Verify database state, not cached Python state |
