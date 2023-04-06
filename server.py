import json
from flask import Flask, render_template, request, redirect, flash, url_for


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    club = [club for club in CLUBS if club['email'] == request.form['email']]
    return render_template('welcome.html', club=club[0], competitions=COMPETITIONS)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = [c for c in CLUBS if c['name'] == club][0]
    found_competition = [c for c in COMPETITIONS if c['name'] == competition][0]
    if found_club and found_competition:
        return render_template('booking.html', club=found_club, competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=COMPETITIONS)


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = [c for c in COMPETITIONS if c['name'] == request.form['competition']][0]
    club = [c for c in CLUBS if c['name'] == request.form['club']][0]
    places_required = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - places_required
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=COMPETITIONS)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
