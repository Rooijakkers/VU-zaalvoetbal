import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from ics import Calendar, Event
from pytz import timezone

team_name = sys.argv[1]
url = f"https://competities.sportcentrumvu.nl/1073-zaalvoetbal.html?action=showTeam&team={team_name}"

page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

MONTHS = {
    "januari": "01",
    "februari": "02",
    "maart": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "augustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "december": "12",
}


def parse_date(string):
    words = string.split(" ")
    year = words[3]
    month = MONTHS[words[2]]
    day = words[1]
    return f"{year}-{month}-{day}"


def create_event(home_team, away_team, referee, location, start_time, date):
    if referee[0:min(len(referee), 17)] == team_name[0:min(len(team_name), 17)]:
        title = f"Fluiten: {home_team} - {away_team}"
    else:
        title = f"Wedstrijd: {home_team} - {away_team}"
    start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    start_datetime = start_datetime.replace(tzinfo=timezone("Europe/Amsterdam"))
    duration = {"minutes": 45}
    description = f"{location}, {start_time}: {title}\nReferee: {referee}"
    return Event(
        name=title,
        begin=start_datetime,
        duration=duration,
        description=description,
        location=location,
    )


calendar = Calendar()
for row in soup.find_all("tr"):
    fields = row.find_all("td")
    # extract date
    if len(fields) == 1:
        date_field = fields[0].text
        if date_field:
            date = parse_date(date_field)
    # extract match info
    elif len(fields) == 6:
        start_time = fields[0].text
        home_team = fields[1].text
        home_team = fields[1].find("a").get("href").split("team=")[1]
        away_team = fields[2].text
        away_team = fields[2].find("a").get("href").split("team=")[1]
        location = fields[3].text
        referee = fields[4].text
        print(start_time, home_team, away_team, location, referee)
        match = create_event(
            home_team=home_team,
            away_team=away_team,
            referee=referee,
            location=location,
            start_time=start_time,
            date=date,
        )
        calendar.events.add(match)


with open(f"{team_name}.ics", "w") as file:
    file.writelines(calendar)
