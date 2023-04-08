import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def load_clubs(file_name):
    with open(file_name) as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions(file_name):
    with open(file_name) as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


app = Flask(__name__)
app.secret_key = 'something_special'

COMPETITIONS = load_competitions('competitions.json')
CLUBS = load_clubs('clubs.json')


def retrieve_club(clubs=CLUBS, value=None):
    if not value:
        return False
    for club in clubs:
        if value in club.values():
            return club
    else:
        return False


def retrieve_competition(competitions=COMPETITIONS, name=None):
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


@app.route('/')
def index():
    return render_template('index.html')


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
        return render_template('booking.html', club=found_club, competition=found_competition, max_places=max_places)
    else:
        flash("Something went wrong-please try again")
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
