import pytest
from rest_framework.test import APIClient

from bookings.models import BookingRequest, Payment


@pytest.mark.django_db
def test_create_booking_success(parent, lsa):
    client = APIClient()

    response = client.post(
        "/api/v1/bookings/",
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "start_time": "2026-08-12T13:00:00Z",
            "end_time": "2026-08-12T14:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 201

    booking = BookingRequest.objects.get(
        id=response.data["id"]
    )

    assert booking.status == BookingRequest.Status.PENDING
    assert booking.payment.status == Payment.Status.PENDING
    assert booking.payment.amount == 1000


@pytest.mark.django_db
def test_booking_rejects_invalid_time(parent, lsa):
    client = APIClient()

    response = client.post(
        "/api/v1/bookings/",
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "start_time": "2026-08-12T14:00:00Z",
            "end_time": "2026-08-12T13:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_booking_rejects_overlap(parent, lsa):
    client = APIClient()

    client.post(
        "/api/v1/bookings/",
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "start_time": "2026-08-12T15:00:00Z",
            "end_time": "2026-08-12T16:00:00Z",
        },
        format="json",
    )

    response = client.post(
        "/api/v1/bookings/",
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "start_time": "2026-08-12T15:30:00Z",
            "end_time": "2026-08-12T16:30:00Z",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "already booked" in str(response.data).lower()