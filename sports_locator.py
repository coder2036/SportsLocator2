from flask import Flask
from flask import request
from bs4 import BeautifulSoup
import requests
import re


app = Flask(__name__)

dates = []
times = []
visiting_teams = []
home_teams = []
games = []

@app.route("/")
def execute():
    # MOVE THIS TO GITHUB AND HEROKu - you can even try to learn branching and stuff
    # . READ IN HTML TO SEND FROM RESULTS.HTML OR JUST SEND
    # THE WHOLE FILE IF POSSIBLE. STORE ENTIRE NBA SCHEDULE IN DATABASE ON HEROKU.
    # MAYBE TRY SOMETHING OTHER THAN MARIADB, PERHAPS POSTRES? ADD FILTERING BY DATE
    # AS WELL, AND OTHER FEATURES IF POSSIBLE/IF YOU THINK OF THEM.
    # Ticketmaster affiliate program once you have a decent prototype.
    load_games()
    ## add filtering by date. add different sports. ticketmaster?
    teams = request.args.getlist("teams")
    locations = request.args.getlist("locations")

    toReturn = """
        <!DOCTYPE HTML>
        <html>
        <head>
          <title>Results</title>
          <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css" integrity="sha384-GJzZqFGwb1QTTN6wy59ffF1BuGJpLSa9DkKMp0DgiMDm4iYMj70gZWKYbI706tWS" crossorigin="anonymous">    <!-- Latest compiled and minified CSS -->
          <link rel="stylesheet" href="static/results-mobile.css">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>Results</h1>
            <hr style="border: .25rem solid black">

        """

    for team in teams:
        toReturn += f"""
        <h1 class="team-name mb-5" style="text-align:center;">{team}' Games</h1>

        <div class="container">
        """
        visiting_indices = [i for i, x in enumerate(visiting_teams) if x == team]
        home_indices = []
        if team in locations:
            home_indices = [i for i, x in enumerate(home_teams) if x == team]

        for index in visiting_indices:
            home_team = home_teams[index]
            if home_team in locations:
                date = dates[index]
                time = times[index]
                visiting_team = visiting_teams[index]
                assert(team == visiting_team)
                game = [date,time,visiting_team,home_team]
                games.append(game)
                # toReturn += "<p>"
                # toReturn += str(game)
                # toReturn += "</p>"

        for index in home_indices:
            date = dates[index]
            time = times[index]
            visiting_team = visiting_teams[index]
            home_team = home_teams[index]
            assert(team == home_team)
            game = [date,time,visiting_team,home_team]
            games.append(game)
            # toReturn += "<p>"
            # toReturn += str(game)
            # toReturn += "</p>"

        # print all qualifying games for this team
        for game in games:
            print(game)
            date = str(game[0])
            time = str(game[1])
            visiting = str(game[2])
            visiting_img = visiting.lower().replace(" ","-")
            visiting_city = visiting.split()[0]
            visiting_mascot = visiting.split()[1]

            home = str(game[3])
            home_img = home.lower().replace(" ","-")
            home_city = home.split()[0]
            home_mascot = home.split()[1]


            toReturn += f"""
            <div class="row text-center">
        <div class="game col-12">
          <div class="row justify-content-center">
            <div class="col-4">
              <span class="team-name"><span class="text-nowrap">{visiting_city}</span><br> {visiting_mascot}</span>
            </div>
            <div class="at col-4 my-auto">
              <span>at</span>
            </div>
            <div class="col-4">
              <span class="team-name"><span class="text-nowrap">{home_city}</span><br> {home_mascot}</span>
            </div>
          </div>
          <div class="row justify-content-center">
            <div class="col-4 my-auto">
              <img src="static/{visiting_img}-logo-vector.png" class="logo img-fluid">
            </div>
            <div class="at col-4 my-auto">
              <div class="row">
                <div class="col-12">
                  <span class="date text-nowrap">{date}</span>
                </div>
              </div>
              <div class="row">
                <div class="col-12">
                  <span class="date text-nowrap">{time}</span>
                </div>
              </div>
              <div class="row">
                <div class="col-12 links my-auto">
                  <div class="row">
                    <div class="col-12">
                      <a class="tickets" href="https://nbatickets.nba.com">Tickets</a>
                    </div>
                    <div class="col-12">
                      <a class="direction" href="https://maps.google.com">Directions</a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-4">
              <img src="static/{home_img}-logo-vector.png" class="logo img-fluid">
            </div>
          </div>
        </div>
      </div>
            """
        toReturn += "</div>" # closes container
        games.clear()

    dates.clear()
    times.clear()
    visiting_teams.clear()
    home_teams.clear()
    # closes container, body, and html
    toReturn += "</body></html>"
    return toReturn

def parse_game(game):
    date = game.find('th').text
    time = game.find_all('td')[0].text
    visiting_team = game.find_all('td')[1].text
    home_team = game.find_all('td')[3].text

    dates.append(date)
    times.append(time)
    visiting_teams.append(visiting_team)
    home_teams.append(home_team)

def load_games():
    res = requests.get("https://www.basketball-reference.com/leagues/NBA_2020_games-january.html")

    if res:
        print("succeeded")
        soup = BeautifulSoup(res.text, 'html.parser')
        # print(soup.prettify())
        games = soup.findAll('table')[0].findAll('tr')

        del games[0]
        for game in games:
            # each game is a <tr> element
            parse_game(game)

        # res.text holds the html
        # month = re.search("((.|\s)+)</tbody>",res.text).groups()[0]
        # print(month)
        # parse_month(month)

    else:
        print("failed")
