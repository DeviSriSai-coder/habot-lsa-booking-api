import pytest
from rest_framework.test import APIClient

from bookings.models import BookingRequest, Payment


@pytest.mark.django_db
def test_payment_webhook_success(parent, lsa):
    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-14T10:00:00Z",
        end_time="2026-08-14T11:00:00Z",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        {
            "booking_id": booking.id,
            "transaction_id": "TXN-SUCCESS-001",
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 200

    booking.refresh_from_db()
    payment = booking.payment

    assert booking.status == BookingRequest.Status.CONFIRMED
    assert payment.status == Payment.Status.SUCCESS
    assert payment.external_transaction_id == "TXN-SUCCESS-001"


@pytest.mark.django_db
def test_payment_webhook_failure(parent, lsa):
    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-14T12:00:00Z",
        end_time="2026-08-14T13:00:00Z",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        {
            "booking_id": booking.id,
            "transaction_id": "TXN-FAILED-001",
            "status": "FAILED",
        },
        format="json",
    )

    assert response.status_code == 200

    booking.refresh_from_db()

    assert booking.status == BookingRequest.Status.FAILED
    assert booking.payment.status == Payment.Status.FAILED


@pytest.mark.django_db
def test_payment_webhook_rejects_invalid_status(parent, lsa):
    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-14T14:00:00Z",
        end_time="2026-08-14T15:00:00Z",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        {
            "booking_id": booking.id,
            "transaction_id": "TXN-INVALID-001",
            "status": "UNKNOWN",
        },
        format="json",
    )

    assert response.status_code == 400