from django.db import models
class Parent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return self.name
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LSAProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    skills = models.ManyToManyField(
        Skill,
        related_name="lsas",
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
class BookingRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    lsa = models.ForeignKey(
        LSAProfile,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(
                fields=["lsa", "start_time", "end_time"]
            ),
            models.Index(
                fields=["status", "start_time"]
            ),
        ]
    def __str__(self):
        return f"Booking #{self.id}"
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
    booking = models.OneToOneField(
        BookingRequest,
        on_delete=models.CASCADE,
        related_name="payment",
    )
    external_transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Payment for Booking #{self.booking_id}"