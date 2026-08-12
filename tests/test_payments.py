from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from bookings.models import BookingRequest
from bookings.payment_service import (
    PaymentGatewayError,
    create_payment,
)


@pytest.mark.django_db
def test_create_payment_success(parent, lsa):
    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-13T10:00:00Z",
        end_time="2026-08-13T11:00:00Z",
    )

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "transaction_id": "TXN-TEST-002",
        "status": "SUCCESS",
    }

    with patch(
        "bookings.payment_service.requests.post",
        return_value=mock_response,
    ) as mock_post:
        result = create_payment(
            booking=booking,
            amount=Decimal("1000.00"),
        )

    assert result["status"] == "SUCCESS"

    mock_post.assert_called_once_with(
        "https://example.com/mock-payment",
        json={
            "booking_id": booking.id,
            "amount": "1000.00",
        },
        timeout=5,
    )


@pytest.mark.django_db
def test_create_payment_gateway_failure(parent, lsa):
    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-13T12:00:00Z",
        end_time="2026-08-13T13:00:00Z",
    )

    import requests

    with patch(
        "bookings.payment_service.requests.post",
        side_effect=requests.RequestException("Gateway unavailable"),
    ):
        with pytest.raises(PaymentGatewayError):
            create_payment(
                booking=booking,
                amount=Decimal("1000.00"),
            )