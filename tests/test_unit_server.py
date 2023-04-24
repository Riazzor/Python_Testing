from datetime import datetime
import pytest
from freezegun import freeze_time

from server import (
    load_clubs, load_competitions, retrieve_club,
    retrieve_competition, control_places,
    check_competition_date_is_in_futur,
    update_club_points, update_competition_places,
    get_club_points_board, set_competition_bookable_field,
)


def test_can_retrieve_list_of_club_from_json(clubs_list, temp_club_file):
    clubs = load_clubs(temp_club_file)
    assert clubs == clubs_list


def test_can_retrieve_list_of_competition_from_json(competitions_list, temp_competition_file):
    competitions = load_competitions(temp_competition_file)
    assert competitions == competitions_list


def test_set_competition_bookable_field_return_updated_competitions_list(competitions_list):
    competitions = set_competition_bookable_field(competitions_list)
    for competition in competitions:
        assert 'bookable' in competition.keys()


@pytest.mark.parametrize(
    'today_date, date_to_check',
    [
        ('2023-03-21', '2023-03-20 10:00:00'),
        ('2024-04-18', '2023-12-20 10:00:00'),
    ]
)
def test_set_competition_bookable_field_fills_with_false_if_date_passed(today_date, date_to_check):
    competitions = [
        {
            'name': 'Test_competition',
            'date': date_to_check,
            'numberOfPlaces': 'Dont care',
        }
    ]
    with freeze_time(today_date):
        competitions = set_competition_bookable_field(competitions)
        assert competitions[0]['bookable'] is False


@pytest.mark.parametrize(
    'today_date, date_to_check',
    [
        ('2023-03-20', '2023-03-21 10:00:00'),
        ('2023-04-18', '2024-12-20 10:00:00'),
    ]
)
def test_set_competition_bookable_field_fills_with_true_if_date_in_futur(today_date, date_to_check):
    competitions = [
        {
            'name': 'Test_competition',
            'date': date_to_check,
            'numberOfPlaces': 'Dont care',
        }
    ]
    with freeze_time(today_date):
        competitions = set_competition_bookable_field(competitions)
        assert competitions[0]['bookable'] is True


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


def test_get_club_points_board(clubs_list):
    club_board = get_club_points_board(clubs_list)
    for club in clubs_list:
        assert {
            'name': club['name'],
            'points': club['points'],
        } in club_board


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
    'required, remaining, points, message_expected',
    [
        ('12', 10, 15, 'Not enough places.'),
        ('12', 13, 10, 'Not enough points.'),
        ('not a number', 120, 15, 'Must require a number : "not a number".'),
        ('0', 120, 15, 'Nothing done.'),
        ('15', 20, 15, '12 places max.'),
    ]
)
def test_requesting_wrong_place_value_return_false(required, remaining, points, message_expected):
    competition = {
        'numberOfPlaces': remaining,
        'bookable': True,
    }
    message, places = control_places(required, competition, points)
    assert message == message_expected
    assert places is False


def test_control_places_return_message_and_remaining_places():
    competition = {
        'numberOfPlaces': 15,
        'bookable': True,
    }

    message, places_remaining = control_places('12', competition, 13)
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
