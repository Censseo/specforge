# Django Models Patterns Reference

## Model Inheritance Strategies

### Abstract Base Classes (Preferred)

```python
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Order(TimestampedModel):
    # Inherits created_at and updated_at
    total = models.DecimalField(max_digits=10, decimal_places=2)
```

Use for shared fields/behavior. No extra database table.

### Multi-Table Inheritance (Avoid)

Creates a JOIN on every query. Only use when you need polymorphic queries across parent table.

### Proxy Models

```python
class ActiveOrder(Order):
    class Meta:
        proxy = True

    objects = ActiveOrderManager()
```

Use for different default managers/methods on the same table.

## Custom QuerySet Patterns

### Chaining

```python
class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published", published_at__lte=timezone.now())

    def by_author(self, author):
        return self.filter(author=author)

    def with_stats(self):
        return self.annotate(
            comment_count=Count("comments"),
            avg_rating=Avg("ratings__score"),
        )

# Chain: Article.objects.published().by_author(user).with_stats()
```

### As Manager

```python
class ArticleManager(models.Manager.from_queryset(ArticleQuerySet)):
    pass

class Article(models.Model):
    objects = ArticleManager()
```

## Field Validation

### Model-Level Validation

```python
class Product(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def clean(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({
                "discount_price": "Discount price must be less than regular price."
            })

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(discount_price__lt=F("price")) | Q(discount_price__isnull=True),
                name="discount_less_than_price",
            ),
            models.UniqueConstraint(
                fields=["sku"],
                name="unique_sku",
            ),
        ]
```

### Field Validators

```python
from django.core.validators import MinValueValidator, RegexValidator

class Product(models.Model):
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    sku = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^[A-Z]{2}-\d{6}$", "SKU format: XX-000000")],
    )
```

## Migration Best Practices

### Data Migrations

```python
def populate_slugs(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    for article in Article.objects.filter(slug=""):
        article.slug = slugify(article.title)
        article.save(update_fields=["slug"])

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
    ]
```

### Safe Migration Patterns

| Operation | Safe? | Notes |
|---|---|---|
| Add nullable field | Yes | No lock, no rewrite |
| Add field with default | Careful | Django 3+ handles in Python, not DB |
| Remove field | Yes | Remove code first, then field |
| Rename field | Careful | Use `RenameField`, not drop+add |
| Add index | Yes | Use `AddIndex` (concurrent on PostgreSQL) |
| Change field type | Dangerous | May rewrite entire table |

### Zero-Downtime Migration Pattern

1. Add new field (nullable)
2. Deploy code that writes to both old and new fields
3. Backfill data migration
4. Deploy code that reads from new field
5. Remove old field

## Soft Delete Pattern

```python
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = SoftDeleteManager()
    all_objects = SoftDeleteQuerySet.as_manager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    class Meta:
        abstract = True
```

## Auditing Pattern

```python
class AuditModel(models.Model):
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True,
        related_name="%(class)s_updated",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```
