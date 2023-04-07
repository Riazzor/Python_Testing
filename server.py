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


def retrieve_competition(competitions=COMPETITIONS, value=None):
    if not value:
        return False
    for competition in competitions:
        if value in competition.values():
            return competition
    else:
        return False


def check_competition_date_is_passed(date):
    competition_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    print(competition_date)
    print(datetime.today())
    return datetime.today() < competition_date


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    club = retrieve_club(clubs=CLUBS, value=request.form['email'])
    competitions = []
    for competition in COMPETITIONS:
        competition['bookable'] = check_competition_date_is_passed(
            competition['date']
        )
        competitions.append(competition)
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition_name>/<club_name>')
def book(competition_name, club_name):
    found_club = retrieve_club(clubs=CLUBS, value=club_name)
    found_competition = retrieve_competition(competitions=COMPETITIONS, value=competition_name)
    if found_club and found_competition:
        return render_template('booking.html', club=found_club, competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club_name, competitions=COMPETITIONS)


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = retrieve_competition(
        competitions=COMPETITIONS,
        value=request.form['competition_name'],
    )
    club = retrieve_club(
        clubs=CLUBS,
        value=request.form['club_name'],
    )
    places_required = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=COMPETITIONS)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
