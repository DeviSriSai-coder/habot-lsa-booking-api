from rest_framework import serializers
from .models import BookingRequest
from .models import LSAProfile
class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = [
            "id",
            "parent",
            "lsa",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]
    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time >= end_time:
            raise serializers.ValidationError(
                "End time must be after start time."
            )
        return attrs
class LSASearchSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = LSAProfile
        fields = [
            "id",
            "name",
            "email",
            "skills",
            "is_active",
        ]