from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from .models import BookingRequest, LSAProfile, Payment


BOOKING_AMOUNT = Decimal("1000.00")
@transaction.atomic
def create_booking(*, parent, lsa, start_time, end_time):
    overlapping_booking = (
        BookingRequest.objects
        .select_for_update()
        .filter(
            lsa=lsa,
            status__in=[
                BookingRequest.Status.PENDING,
                BookingRequest.Status.CONFIRMED,
            ],
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        .first()
    )

    if overlapping_booking:
        raise ValidationError(
            "The selected LSA is already booked for this time."
        )

    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time=start_time,
        end_time=end_time,
    )

    Payment.objects.create(
        booking=booking,
        amount=BOOKING_AMOUNT,
        status=Payment.Status.PENDING,
    )

    return booking
def search_available_lsas(*, skill, start_time=None, end_time=None):
    queryset = (
        LSAProfile.objects
        .filter(
            is_active=True,
            skills__name__iexact=skill,
        )
        .prefetch_related("skills")
        .distinct()
    )

    if start_time and end_time:
        conflicting_lsa_ids = (
            BookingRequest.objects
            .filter(
                status__in=[
                    BookingRequest.Status.PENDING,
                    BookingRequest.Status.CONFIRMED,
                ],
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            .values_list("lsa_id", flat=True)
        )

        queryset = queryset.exclude(
            id__in=conflicting_lsa_ids
        )

    return queryset