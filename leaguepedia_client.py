import mwclient
import os
from dotenv import load_dotenv
from mwrogue.esports_client import EsportsClient

def get_tournament(leagues):

    site = mwclient.Site('lol.fandom.com', path='/')

    site.login(
        username=os.getenv("LEAGUEPEDIA_USER"),
        password=os.getenv("LEAGUEPEDIA_PASSWORD")
    )
    
    query_api = site.api("cargoquery",
        limit='max',
        tables = 'CurrentLeagues=CL',
        fields = 'CL.Event,CL.OverviewPage,CL.Priority'
    )

    list_current_tournaments = []
    for i in query_api["cargoquery"]:
        for league in leagues:
            if league in i["title"]['OverviewPage']:
                list_current_tournaments.append([i["title"]['Event'], i["title"]['OverviewPage']])

    return list_current_tournaments

def get_upcoming_matches(leagues):

    site = mwclient.Site('lol.fandom.com', path='/')

    site.login(
        username=os.getenv("LEAGUEPEDIA_USER"),
        password=os.getenv("LEAGUEPEDIA_PASSWORD")
    )

    filter = ""
    for tournament in leagues:
        if filter != "":
            filter += " OR "
        filter += f'MS.OverviewPage = "{tournament}"'

    query_api = site.api("cargoquery",
        limit='max',
        tables = 'MatchSchedule=MS',
        fields = 'MS.Team1,MS.Team2, MS.DateTime_UTC, MS.BestOf, MS.Stream, MS.MatchId',
        where = f'({filter}) AND MS.Winner IS NULL AND MS.Team1 != "TBD" AND MS.Team2 != "TBD"',
        order_by = 'MS.DateTime_UTC ASC'
    )

    response = []
    for i in query_api["cargoquery"]:
        response.append({
            'team1': i['title']['Team1'],
            'team2': i['title']['Team2'],
            'datetime_utc': i['title']['DateTime UTC'],
            'best_of': i['title']['BestOf'],
            'stream': i['title']['Stream'],
            'match_id': i['title']['MatchId']
        })

    return response

if __name__ == "__main__":

    load_dotenv()
    

    tournament = get_tournament(["LEC"])
    # print(tournament)
    matches = get_upcoming_matches([t[1] for t in tournament])
    for i in matches:
        print(i)