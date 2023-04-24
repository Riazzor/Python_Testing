import json
import os
import pytest
from server import create_app
from freezegun import freeze_time


@pytest.fixture
def temp_club_file():
    """
    Custom tempfile fixture. The reason is that the NamedTemporaryFile
    was removed with garbage collection during the create_app process.
    TemporaryDirectory was fine but the name created contained an uuid
    in it, rendering it unusable with the current app's config creation.
    """
    if not os.path.exists('./tests/fixtures/tempdir'):
        os.mkdir('./tests/fixtures/tempdir')
    club_temp_file = open('./tests/fixtures/tempdir/club_temp_file.json', 'x')
    club_temp_file.close()
    with open('tests/fixtures/clubs_test.json') as file:
        content = json.load(file)
    with open('tests/fixtures/tempdir/club_temp_file.json', 'w') as file:
        json.dump(content, file)

    try:
        club_temp_file = open('tests/fixtures/tempdir/club_temp_file.json', 'a+')
        yield club_temp_file.name
    except Exception:
        raise
    finally:
        club_temp_file.close()
        if os.path.exists('tests/fixtures/tempdir'):
            for file in os.listdir('tests/fixtures/tempdir'):
                os.remove(f'./tests/fixtures/tempdir/{file}')
            os.rmdir('tests/fixtures/tempdir')


@pytest.fixture
def temp_competition_file():
    """
    Custom tempfile fixture. The reason is that the NamedTemporaryFile
    was removed with garbage collection during the create_app process.
    TemporaryDirectory was fine but the name created contained an uuid
    in it, rendering it unusable with the current app's config creation.
    """
    if not os.path.exists('./tests/fixtures/tempdir'):
        os.mkdir('./tests/fixtures/tempdir')
    competition_temp_file = open('./tests/fixtures/tempdir/competition_temp_file.json', 'x')
    competition_temp_file.close()
    with open('tests/fixtures/competitions_test.json') as file:
        content = json.load(file)
    with open('tests/fixtures/tempdir/competition_temp_file.json', 'w') as file:
        json.dump(content, file)

    try:
        competition_temp_file = open('tests/fixtures/tempdir/competition_temp_file.json', 'a+')
        yield competition_temp_file.name
    except Exception:
        raise
    finally:
        competition_temp_file.close()
        if os.path.exists('tests/fixtures/tempdir'):
            for file in os.listdir('tests/fixtures/tempdir'):
                os.remove(f'./tests/fixtures/tempdir/{file}')
            os.rmdir('tests/fixtures/tempdir')


@pytest.fixture
def client(temp_club_file, temp_competition_file):
    # Unless specified, make sure the now date is before the competition date.
    with freeze_time('2019-10-10'):
        app = create_app()
        with app.test_client() as client:
            yield client


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
        {
            "name": "test 3",
            "email": "test3@email.uk",
            "points": "12",
        },
        {
            "name": "test 4",
            "email": "test4@email.fr",
            "points": "15",
        },
        {
            "name": "test 5",
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
            "numberOfPlaces": "5"
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


