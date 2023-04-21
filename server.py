import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime
from config import config


def load_clubs(file_name):
    with open(file_name) as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions(file_name):
    with open(file_name) as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


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


def control_places(places_required, competition, points_remaining):
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
    if places_required > places_remaining:
        message = 'Not enough places.'
        result = False
    elif places_required == 0:
        message = 'Nothing done.'
        result = False
    elif places_required > 12:
        message = '12 places max.'
        result = False
    elif places_required > points_remaining:
        message = 'Not enough points.'
        result = False
    else:
        message = 'Great-booking complete!'
        result = places_remaining - places_required

    return message, result


def update_club_points(club, places_required):
    club['points'] = int(club['points']) - places_required
    club['points'] = str(club['points'])


def update_competition_places(competition, places_required):
    places_remaining = int(competition['numberOfPlaces'])
    competition['numberOfPlaces'] = str(places_remaining - places_required)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)

    COMPETITIONS = load_competitions(
        app.config['PATH'].get('competitions')
    )
    CLUBS = load_clubs(
        app.config['PATH'].get('clubs')
    )

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
        message, places_remaining = control_places(
            request.form['places'],
            competition,
            int(club['points']),
        )
        flash(message)
        if places_remaining is not False:
            places_required = int(request.form['places'])
            update_competition_places(competition, places_required)
            update_club_points(club, places_required)
        return render_template('welcome.html', club=club, competitions=competitions)

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))
    return app


app = create_app()
