from server import load_clubs, retrieve_club, load_competitions, retrieve_competition


def test_user_path(client, clubs_list, club, competition, temp_club_file, temp_competition_file):
    # User goes to the home page with the club points board :
    response = client.get('/')
    for cl in clubs_list:
        assert cl['name'].encode() in response.data
        assert cl['points'].encode() in response.data

    # User connect to the app :
    response = client.post(
        '/showSummary',
        data={
            'email': f"{club['email']}"
        }
    )
    club_points = int(club['points'])
    competition_places = int(competition['numberOfPlaces'])
    assert (f'Points available: {club_points}').encode() in response.data

    # User tries to buy more than 12 places :
    response = client.post(
        '/purchasePlaces',
        data={
            'club_name': 'test 1',
            'competition_name': 'Test competition 1',
            'places': '13',
        },
    )
    assert b'12 places max.' in response.data

    # User books 5 places :
    response = client.post(
        '/purchasePlaces',
        data={
            'club_name': 'test 1',
            'competition_name': 'Test competition 1',
            'places': '5',
        },
    )
    assert f'Points available: {club_points - 5}'.encode() in response.data
    assert b'Great-booking complete!' in response.data
    clubs = load_clubs(temp_club_file)
    club = retrieve_club(clubs, 'test 1')
    assert club['points'] == str(club_points - 5)

    competitions = load_competitions(temp_competition_file)
    competition = retrieve_competition(competitions, 'Test competition 1')
    assert competition['numberOfPlaces'] == str(competition_places - 5)
    assert competition['booked_places'] == {
        club['name']: 5,
    }

    # User logout :
    response = client.get('/logout', follow_redirects=True)
    assert b'Registration Portal!' in response.data
    assert response.status_code == 200
