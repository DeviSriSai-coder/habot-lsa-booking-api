import pytest

from bookings.models import Parent, LSAProfile, Skill


@pytest.fixture
def parent():
    return Parent.objects.create(
        name="Test Parent",
        email="testparent@example.com",
        phone="9999999999",
    )


@pytest.fixture
def lsa():
    lsa = LSAProfile.objects.create(
        name="Test LSA",
        email="testlsa@example.com",
        is_active=True,
    )

    skill = Skill.objects.create(name="ADHD")
    lsa.skills.add(skill)

    return lsa