from server import load_clubs, load_competitions, retrieve_club

import pytest


@pytest.fixture
def clubs_test():
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
def competitions_test():
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


def test_can_retrieve_list_of_club_from_json(clubs_test):
    clubs = load_clubs('tests/fixtures/clubs_test.json')
    assert clubs == clubs_test


def test_can_retrieve_list_of_competition_from_json(competitions_test):
    competitions = load_competitions('tests/fixtures/competitions_test.json')
    assert competitions == competitions_test


def test_can_retrieve_club_by_name(clubs_test):
    club = retrieve_club(clubs=clubs_test, value='test 1')
    assert club['email'] == 'test@email.co'


def test_can_retrieve_club_by_email(clubs_test):
    club = retrieve_club(clubs=clubs_test, value='test@email.co')
    assert club['name'] == 'test 1'


def test_retrieve_club_with_wrong_entry_return_false(clubs_test):
    club1 = retrieve_club(clubs=clubs_test, value='wrong test name')
    club2 = retrieve_club(clubs=clubs_test, value='wrongtest@email.co')
    assert club1 is False
    assert club2 is False
