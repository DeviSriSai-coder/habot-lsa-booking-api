import logging
import requests
from django.conf import settings
logger = logging.getLogger(__name__)
class PaymentGatewayError(Exception):
    """Raised when the external payment gateway fails."""
def create_payment(*, booking, amount):
    gateway_url = getattr(
        settings,
        "PAYMENT_GATEWAY_URL",
        "https://example.com/mock-payment",
    )
    payload = {
        "booking_id": booking.id,
        "amount": str(amount),
    }
    try:
        response = requests.post(
            gateway_url,
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception(
            "Payment gateway request failed for booking %s",
            booking.id,
        )
        raise PaymentGatewayError(
            "Unable to contact payment gateway."
        ) from exc
    return response.json()