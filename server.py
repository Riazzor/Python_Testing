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


def retrieve_club(clubs, value=None):
    if not value:
        return False
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


def retrieve_competition(competitions, name=None):
    if not name:
        return False
    for competition in competitions:
        if name == competition['name']:
            return competition
    else:
        return False


def control_places(places_required, places_remaining):
    """
    Few control on the required places from the post request.
    Check that it's a number between 1 and the number of points.

    return the error message and False otherwise
    """
    if not places_required.isnumeric():
        message = f'Must require a number : "{places_required}".'
        return message, False

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
    else:
        message = 'Great-booking complete!'
        result = places_remaining - places_required

    return message, result


def check_competition_date_is_in_futur(date):
    competition_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return datetime.today() < competition_date


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
        club = retrieve_club(clubs=CLUBS, value=request.form['email'])
        if not club:
            return render_template('index.html', error='Email does not exist !')

        competitions = []
        for competition in COMPETITIONS:
            competition['bookable'] = check_competition_date_is_in_futur(
                competition['date']
            )
            competitions.append(competition)
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
        competition = retrieve_competition(
            competitions=COMPETITIONS,
            name=request.form['competition_name'],
        )
        club = retrieve_club(
            clubs=CLUBS,
            value=request.form['club_name'],
        )
        message, places_remaining = control_places(request.form['places'], int(competition['numberOfPlaces']))
        flash(message)
        if places_remaining is not False:
            places_required = int(request.form['places'])
            update_competition_places(competition, places_required)
            update_club_points(club, places_required)
        return render_template('welcome.html', club=club, competitions=COMPETITIONS)

    # TODO: Add route for points display

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))
    return app


app = create_app()
