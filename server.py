import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime
from config import config


def load_clubs(file_name):
    with open(file_name) as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def save_club(file_name, club):
    with open(file_name) as fp:
        clubs = json.load(fp).get('clubs', [])

    for i, cl in enumerate(clubs):
        if cl['name'] == club['name']:
            clubs[i] = club
            break

    with open(file_name, 'w') as fp:
        json.dump(
            {'clubs': clubs},
            fp,
        )


def load_competitions(file_name):
    with open(file_name) as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


def save_competition(file_name, competition):
    with open(file_name) as fp:
        competitions = json.load(fp).get('competitions', [])

    for i, comp in enumerate(competitions):
        if comp['name'] == competition['name']:
            competitions[i] = competition
            break

    with open(file_name, 'w') as fp:
        json.dump(
            {'competitions': competitions},
            fp,
        )


def booked_place_state(club_name, competition):
    """
    Each time a club books places, the number are stored in competition file.
    """
    competition_booked_places = competition.get('booked_places', {})
    club_booked_places = int(competition_booked_places.get(club_name, 0))
    return club_booked_places


def check_competition_date_is_in_futur(date):
    competition_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return datetime.today() < competition_date


def set_competition_bookable_field(list_of_competitions):
    """
    Competition is only bookable if the date is in future.
    Return a copy of the list.
    """
    competitions = []
    for comp in list_of_competitions:
        competition = comp.copy()
        competition['bookable'] = check_competition_date_is_in_futur(
            competition['date']
        )
        competitions.append(competition)
    return competitions


def retrieve_club(clubs, value):
    for club in clubs:
        if value in club.values():
            return club
    else:
        return False


def get_club_points_board(clubs):
    club_board = []
    for club in clubs:
        club_board.append(
            {'name': club['name'], 'points': club['points']}
        )
    return club_board


def retrieve_competition(competitions, name):
    for competition in competitions:
        if name == competition['name']:
            return competition
    else:
        return False


def control_places(places_booked, places_required, competition, points_remaining):
    """
    Few control on the required places from the post request.
    Check that it's a number between 1 and the number of points,
    less than the number of places, less than 12 places per club.

    return the error message and False otherwise
    """
    if not places_required.isnumeric():
        return (
            f'Must require a number : "{places_required}".',
            False
        )
    if not competition['bookable']:
        return (
            'Competition is not bookable',
            False
        )
    places_remaining = int(competition['numberOfPlaces'])

    places_required = int(places_required)
    result = False
    if places_remaining == 0 or places_booked == 12:
        message = 'No more places.'
    elif places_required > places_remaining:
        message = 'Not enough places.'
    elif places_required == 0:
        message = 'Nothing done.'
    elif places_required > (12 - places_booked):
        message = '12 places max.'
    elif places_required > points_remaining:
        message = 'Not enough points.'
    else:
        message = 'Great-booking complete!'
        result = places_remaining - places_required

    return message, result


def update_club(club, places_required):
    club['points'] = int(club['points']) - places_required
    club['points'] = str(club['points'])


def update_competition(competition, places_required, club_name):
    places_remaining = int(competition['numberOfPlaces'])
    booked_places = competition.get('booked_places', {})
    booked_places[club_name] = places_required + booked_places.get(club_name, 0)

    competition['booked_places'] = booked_places
    competition['numberOfPlaces'] = str(places_remaining - places_required)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)

    competitions_file_name = app.config['PATH'].get('competitions')
    clubs_file_name = app.config['PATH'].get('clubs')

    CLUBS = load_clubs(clubs_file_name)
    COMPETITIONS = load_competitions(competitions_file_name)

    @app.route('/')
    def index():
        clubs = CLUBS
        # Only clubs name and points are used :
        club_points_board = get_club_points_board(clubs)
        return render_template('index.html', club_board=club_points_board)

    @app.route('/showSummary', methods=['POST'])
    def show_summary():
        competitions = set_competition_bookable_field(COMPETITIONS)
        club = retrieve_club(clubs=CLUBS, value=request.form['email'])
        if not club:
            return render_template('index.html', error='Email does not exist !')

        return render_template('welcome.html', club=club, competitions=competitions)

    @app.route('/book/<competition_name>/<club_name>')
    def book(competition_name, club_name):
        found_club = retrieve_club(clubs=CLUBS, value=club_name)
        found_competition = retrieve_competition(competitions=COMPETITIONS, name=competition_name)
        if found_club and found_competition:
            max_places = int(found_competition['numberOfPlaces'])
            if max_places > 12:
                max_places = 12
            return render_template(
                'booking.html',
                club=found_club,
                competition=found_competition,
                max_places=max_places,
            )
        else:
            flash('Club or competition does not exist.')
            return render_template('welcome.html', club=club_name, competitions=COMPETITIONS)

    @app.route('/purchasePlaces', methods=['POST'])
    def purchase_places():
        competitions = set_competition_bookable_field(COMPETITIONS)
        competition = retrieve_competition(
            competitions=competitions,
            name=request.form['competition_name'],
        )
        club = retrieve_club(
            clubs=CLUBS,
            value=request.form['club_name'],
        )
        places_booked = booked_place_state(club['name'], competition)
        message, places_remaining = control_places(
            places_booked,
            request.form['places'],
            competition,
            int(club['points']),
        )
        flash(message)
        if places_remaining is not False:
            places_required = int(request.form['places'])
            update_competition(competition, places_required, club['name'])
            update_club(club, places_required)
            save_competition(competitions_file_name, competition)
            save_club(clubs_file_name, club)
        return render_template('welcome.html', club=club, competitions=competitions)

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))
    return app


if __name__ == '__main__':
    app = create_app()
