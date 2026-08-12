import pytest
from rest_framework.test import APIClient

from bookings.models import BookingRequest


@pytest.mark.django_db
def test_search_lsa_by_skill(lsa):
    client = APIClient()

    response = client.get(
        "/api/v1/lsas/search/",
        {
            "skill": "ADHD",
            "start_time": "2026-08-12T17:00:00Z",
            "end_time": "2026-08-12T18:00:00Z",
        },
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == lsa.id


@pytest.mark.django_db
def test_search_excludes_booked_lsa(parent, lsa):
    BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        start_time="2026-08-12T17:00:00Z",
        end_time="2026-08-12T18:00:00Z",
    )

    client = APIClient()

    response = client.get(
        "/api/v1/lsas/search/",
        {
            "skill": "ADHD",
            "start_time": "2026-08-12T17:30:00Z",
            "end_time": "2026-08-12T18:30:00Z",
        },
    )

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_search_requires_skill():
    client = APIClient()

    response = client.get(
        "/api/v1/lsas/search/",
        {
            "start_time": "2026-08-12T17:00:00Z",
            "end_time": "2026-08-12T18:00:00Z",
        },
    )

    assert response.status_code == 400