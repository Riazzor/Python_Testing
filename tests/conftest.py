import pytest


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


