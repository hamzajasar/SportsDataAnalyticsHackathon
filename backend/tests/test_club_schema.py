import pytest
from pydantic import ValidationError

from app.schemas.club import ClubProfile, ClubRequest
from app.services import actions


def test_sample_club_matches_profile_format():
    club = ClubProfile.model_validate(actions.sample_club())
    assert club.children > 0 and club.electricity_kwh_year.heating >= 0


def test_request_defaults_to_sample_club():
    assert ClubRequest().club is None


def test_rejects_invalid_values():
    data = actions.sample_club()
    with pytest.raises(ValidationError):
        ClubProfile.model_validate({**data, "children": 0})
    with pytest.raises(ValidationError):
        ClubProfile.model_validate({**data, "lat": 0})
