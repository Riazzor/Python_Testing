import pytest
from freezegun import freeze_time

from server import (
    load_clubs, load_competitions, retrieve_club,
    retrieve_competition, control_places,
    check_competition_date_is_in_futur,
    update_club_points, update_competition_places,
)


@pytest.fixture
def clubs_list():
    yield [
        {
            "name": "test 1",
            "email": "test@email.co",
            "points": "13",
        },
        {
            "name": "test 2",
            "email": "test2@email.com",
            "points": "4",
        },
        {"name": "test 3",
         "email": "test3@email.uk",
         "points": "12",
         },
        {
            "name": "test 4",
            "email": "test4@email.fr",
            "points": "15",
        },
        {"name": "test 5",
         "email": "test5@email.de",
         "points": "17",
         },
    ]


@pytest.fixture
def club():
    yield {
        "name": "test 1",
        "email": "test@email.co",
        "points": "13",
    }


@pytest.fixture
def competitions_list():
    yield [
        {
            "name": "Test competition 1",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Test competition 2",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        },
        {
            "name": "Test competition 3",
            "date": "2022-03-25 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Test competition 4",
            "date": "2021-11-23 13:30:00",
            "numberOfPlaces": "13"
        },
        {
            "name": "Test competition 5",
            "date": "2023-04-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Test competition 6",
            "date": "2022-10-22 13:30:00",
            "numberOfPlaces": "13"
        },
    ]


@pytest.fixture
def competition():
    yield {
        "name": "Test competition 1",
        "date": "2020-03-27 10:00:00",
        "numberOfPlaces": "25"
    }


def test_can_retrieve_list_of_club_from_json(clubs_list):
    clubs = load_clubs('tests/fixtures/clubs_test.json')
    assert clubs == clubs_list


def test_can_retrieve_list_of_competition_from_json(competitions_list):
    competitions = load_competitions('tests/fixtures/competitions_test.json')
    assert competitions == competitions_list


@pytest.mark.parametrize(
    'value_input, field_to_test, expected_result',
    [
        ('test 1', 'email', 'test@email.co'),
        ('test@email.co', 'name', 'test 1'),
    ]
)
def test_can_retrieve_club_with_value(clubs_list, value_input, field_to_test, expected_result):
    club = retrieve_club(clubs=clubs_list, value=value_input)
    assert club[field_to_test] == expected_result


@pytest.mark.parametrize(
    'name_input, field_to_test, expected_result',
    [
        ('Test competition 1', 'date', '2020-03-27 10:00:00'),
        ('Test competition 3', 'date', '2022-03-25 10:00:00'),
    ]
)
def test_can_retrieve_competition_with_name(competitions_list, name_input, field_to_test, expected_result):
    competition = retrieve_competition(competitions=competitions_list, name=name_input)
    assert competition[field_to_test] == expected_result


@pytest.mark.parametrize(
    'value_input',
    [
        'wrong test name',
        'wrongtest@email.co',
    ]
)
def test_retrieving_club_with_wrong_entry_return_false(clubs_list, value_input):
    club = retrieve_club(clubs=clubs_list, value=value_input)
    assert club is False


@pytest.mark.parametrize(
    'name_input',
    [
        'wrong test name',
        'wrongtest@email.co',
    ]
)
def test_retrieving_competition_with_wrong_name_return_false(competitions_list, name_input):
    competition = retrieve_competition(competitions=competitions_list, name=name_input)
    assert competition is False


@pytest.mark.parametrize(
    'required, remaining, message_expected',
    [
        ('123', 120, 'Not enough places.'),
        ('not a number', 120, 'Must require a number : "not a number".'),
        ('0', 120, 'Nothing done.'),
        ('15', 20, '12 places max.'),
    ]
)
def test_requesting_wrong_place_value_return_false(required, remaining, message_expected):
    message, places = control_places(places_required=required, places_remaining=remaining)
    assert message == message_expected
    assert places is False


def test_control_places_return_message_and_remaining_places():
    message, places_remaining = control_places('12', 15)
    assert message == 'Great-booking complete!'
    assert places_remaining == 3


@pytest.mark.parametrize(
    'date_to_check, now_date, expected_result',
    [
        ('2019-12-24 10:00:00', '2018-10-21', True),
        ('2019-12-24 10:00:00', '2019-12-25', False),
    ]
)
def test_check_competition_date_control_if_date_is_before_or_after_today(date_to_check, now_date, expected_result):
    with freeze_time(now_date):
        date_is_after_today = check_competition_date_is_in_futur(date_to_check)
        assert date_is_after_today is expected_result


def test_updating_points_remove_club_points(club):
    assert club['points'] == '13'
    update_club_points(club=club, places_required=10)
    assert club['points'] == '3'


def test_updating_places_remove_competition_places(competition):
    assert competition['numberOfPlaces'] == '25'
    update_competition_places(competition=competition, places_required=12)
    assert competition['numberOfPlaces'] == '13'
