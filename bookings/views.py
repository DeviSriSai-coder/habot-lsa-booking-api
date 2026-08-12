import logging
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    BookingCreateSerializer,
    LSASearchSerializer,
)
from .services import (
    create_booking,
    search_available_lsas,
)
from django.utils.dateparse import parse_datetime
from .models import BookingRequest,Payment
class BookingCreateView(APIView):
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = create_booking(
            parent=serializer.validated_data["parent"],
            lsa=serializer.validated_data["lsa"],
            start_time=serializer.validated_data["start_time"],
            end_time=serializer.validated_data["end_time"],
        )
        response_serializer = BookingCreateSerializer(booking)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
class LSASearchView(APIView):

    def get(self, request):
        skill = request.query_params.get("skill")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")

        if not skill:
            return Response(
                {"error": "skill query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not start_time or not end_time:
            return Response(
                {
                    "error": (
                        "start_time and end_time "
                        "query parameters are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_time = parse_datetime(start_time)
        end_time = parse_datetime(end_time)

        if not start_time or not end_time:
            return Response(
                {"error": "Invalid datetime format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_time >= end_time:
            return Response(
                {"error": "end_time must be after start_time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lsas = search_available_lsas(
            skill=skill,
            start_time=start_time,
            end_time=end_time,
        )

        serializer = LSASearchSerializer(
            lsas,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
logger = logging.getLogger(__name__)
class PaymentWebhookView(APIView):
    @transaction.atomic
    def post(self, request):
        booking_id = request.data.get("booking_id")
        transaction_id = request.data.get("transaction_id")
        payment_status = request.data.get("status")

        if not booking_id or not transaction_id or not payment_status:
            return Response(
                {"error": "booking_id, transaction_id and status are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking = (
                BookingRequest.objects
                .select_for_update()
                .get(id=booking_id)
            )
        except BookingRequest.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                "external_transaction_id": transaction_id,
                "amount": 0,
            },
        )

        # Idempotency: don't process the same successful payment twice.
        if (
            payment.status == Payment.Status.SUCCESS
            and payment.external_transaction_id == transaction_id
        ):
            return Response(
                {"message": "Payment already processed."},
                status=status.HTTP_200_OK,
            )

        payment.external_transaction_id = transaction_id

        if payment_status == "SUCCESS":
            payment.status = Payment.Status.SUCCESS
            booking.status = BookingRequest.Status.CONFIRMED

        elif payment_status == "FAILED":
            payment.status = Payment.Status.FAILED

        else:
            return Response(
                {"error": "Invalid payment status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.save()
        booking.save(update_fields=["status", "updated_at"])

        logger.info(
            "Payment webhook processed: booking=%s status=%s",
            booking.id,
            payment_status,
        )

        return Response(
            {
                "booking_id": booking.id,
                "payment_status": payment.status,
                "booking_status": booking.status,
            },
            status=status.HTTP_200_OK,
        )