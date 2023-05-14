import pytest

from server import (
    load_competitions,
    load_clubs,
    retrieve_competition,
    retrieve_club,
)


def test_index_endpoint_display_the_welcome_page(client):
    response = client.get('/')
    assert b'<h1>Welcome to the GUDLFT Registration Portal!</h1>' in response.data


def test_index_endpoint_display_the_club_points_board(client, clubs_list):
    response = client.get('/')
    for club in clubs_list:
        assert f"<td>{club['name']}</td>".encode() in response.data
        assert f"<td>{club['points']}</td>".encode() in response.data


@pytest.mark.parametrize(
    'email, points',
    [
        ('test@email.co', '13'),
        ('test3@email.uk', '12'),
    ]
)
def test_show_summary_endpoint_display_competitions_and_points(client, competitions_list, email, points):
    response = client.post(
        '/showSummary',
        data={
            'email': f'{email}'
        }
    )
    assert ('Points available: %s' % points).encode() in response.data

    # All the competition must be displayed :
    for competition in competitions_list:
        assert competition['name'].encode() in response.data
        assert ('Number of Places: %s' % competition['numberOfPlaces']).encode() in response.data


def test_show_summary_endpoint_with_wrong_email_redirects_with_error_message(client):
    response = client.post(
        '/showSummary',
        data={
            'email': 'not_a_valid@email.com'
        }
    )
    # Redirected to login page
    assert b'<h1>Welcome to the GUDLFT Registration Portal!</h1>' in response.data

    # Error message on page
    assert b'Email does not exist !' in response.data


def test_book_endpoint_display_form_with_availables_places(client, club, competition):
    response = client.get(f'/book/{competition["name"]}/{club["name"]}',)
    assert ('Places available: %s' % competition['numberOfPlaces']).encode() in response.data


@pytest.mark.parametrize(
    'competition_name, club_name',
    [
        ('Test competition 1', 'wrong club name'),
        ('wrong competition name', 'test 1'),
        ('wrong name', 'for both'),
    ],
)
def test_book_endpoint_wrong_club_or_competition_redirect_to_welcome(
    client,
    competition_name,
    club_name,
):
    response = client.get(f'/book/{competition_name}/{club_name}',)
    assert b'Club or competition does not exist.' in response.data


def test_purchase_place_update_points_and_places(client, competitions_list, clubs_list):
    club = retrieve_club(clubs=clubs_list, value='test 1')
    competition = retrieve_competition(competitions=competitions_list, name='Test competition 1')
    assert club['points'] == '13'
    assert competition['numberOfPlaces'] == '25'

    response = client.post(
        '/purchasePlaces',
        data={
            'club_name': 'test 1',
            'competition_name': 'Test competition 1',
            'places': '10',
        },
    )
    assert response.status_code == 200

    # Not having a database might sound like a good idea but it's just
    # a pain for testing... So we have to check the presence of the string in the response.
    # Just know that there are no competition with 15 places
    # and no club with 3 points in the test data.
    assert b'Points available: 3' in response.data
    assert b'Number of Places: 15' in response.data

    # Just in case, make sure there is only the updated competition and club with those numbers
    # as the response is the list of competition
    assert response.data.count(b'Number of Places: 15') == 1
    assert response.data.count(b'Points available: 3') == 1


@pytest.mark.parametrize(
    'competition_name, place_number, expected_message',
    [
        ('Test competition 1', '13', '12 places max.'),
        ('Test competition 2', '7', 'Not enough places.'),
        ('Test competition 2', '0', 'Nothing done.')
    ]
)
def test_purchase_place_endpoint_with_wrong_condition_redirects(
        client, competition_name,
        place_number, expected_message,
):
    response = client.post(
        '/purchasePlaces',
        data={
            'club_name': 'test 2',
            'competition_name': competition_name,
            'places': place_number,
        },
    )
    assert expected_message.encode() in response.data


def test_purchase_place_endpoint_update_files(client, competition, club, temp_club_file, temp_competition_file):
    old_club_points = int(club['points'])
    old_competition_places = int(competition['numberOfPlaces'])

    response = client.post(
        '/purchasePlaces',
        data={
            'club_name': club['name'],
            'competition_name': competition['name'],
            'places': 10,
        },
    )
    assert response.status_code == 200
    competitions = load_competitions(temp_competition_file)
    clubs = load_clubs(temp_club_file)
    competition = retrieve_competition(competitions, competition['name'])
    club = retrieve_club(clubs, club['name'])
    assert int(club['points']) == old_club_points - 10
    assert int(competition['numberOfPlaces']) == old_competition_places - 10
    assert competition['booked_places'] == {
        club['name']: 10,
    }


def test_logout_endpoint_redirect_to_index(client):
    response = client.get('/logout')
    assert response.headers['Location'] == '/'  # url of index page

    response = client.get('/logout', follow_redirects=True)
    assert b'Registration Portal!' in response.data
