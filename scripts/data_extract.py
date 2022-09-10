import os
import pandas as pd
import datetime
import time
from riotwatcher import LolWatcher

#Start of timer
start_time = time.time()


def get_head(games_rank_inf:dict) -> list:
    """
    Returns the keywords/headings of each column
    """
    headers = []
    for data in games_rank_inf:
        if data == 'info':
            for dat in games_rank_inf[data]:
                if dat == 'participants':
                    for row in games_rank_inf[data][dat]:
                        for head in row:
                            if not head in headers:
                                headers.append(head)
    return headers


def date_conversion(date:list) -> list:
    """
    Convert date string to epoch time
    
    date: list date
    retrun: date list int epoch format, [start, end]
    """ 
    format = '%Y/%m/%d'
    date_ini = date[0]
    date_fn = date[1]
    epoch = datetime.datetime(1970, 1, 1)
    epoch_ini = int ((datetime.datetime.strptime(date_ini, format) - epoch).total_seconds())
    epoch_fn = int ((datetime.datetime.strptime(date_fn, format) - epoch).total_seconds())
    return [epoch_ini, epoch_fn]

def name_server(region:str) -> list:
    """
    Provide the server name and region for the correct use of the API

    region: user region
    return: List with server name and region
    """
    region = region.upper()
    servers = {
            'BR':['BR1', 'AMERICAS'], 'NA':['NA1','AMERICAS'], 'LAN':['LA1', 'AMERICAS'], 'LAS':['LA2', 'AMERICAS'],
            'KR':['KR', 'ASIA '], 'JP': ['JP1', 'ASIA'],
            'EUN':['EUN1', 'EUROPE '], 'EUW':['EUW1', 'EUROPE'], 'TR':['TR1', 'EUROPE'], 'RU':['RU', 'EUROPE'],
            'OCE':['OC1','SEA']
            }
    for server in servers:
        if server == region:
            return servers[server]

def pick_games(token:str, user:str, data_server:list, date:list) -> list:
    """
    Select the games that will be analyzed
    Extract all the information of the game

    token: Code provided by riot developer
    user: Username
    data_server: list with region and server
    date: start and end date
    return: game lists
    """
    #token:  Token provided by the company
            #20 requests every 1 second(s)
            #100 requests every 2 minute(s)
    try:
        #API connection
        lol_watcher = LolWatcher(token)
        region = data_server[0]

        #User data
        usuario = lol_watcher.summoner.by_name(region, user)

        #Date conversion
        date_c = date_conversion(date)
        
        #List of games in ranker (420 = Solo/Q, 440 = Flex)
        list_games_rank = lol_watcher.match.matchlist_by_puuid(region,usuario['puuid'],0,100,420,'ranked',date_c[0],date_c[1])

        return list_games_rank
    except:
        print("¡Verifica tu token y vuelve a intentar!")


def game_data(token:str, data_server:list, list_games_rank:list) -> list:
    """
    Extract all the information of the game

    token: Code provided by riot developer
    user: Username
    server: list with region and server
    return: game data list
    """
     #token:  Token provided by the company
            #20 requests every 1 second(s)
            #100 requests every 2 minute(s)

    #API connection
    lol_watcher = LolWatcher(token)
    server = data_server[1]

    data_games=[]
    for game in list_games_rank:
        #Ranker games information
        games_rank_inf = lol_watcher.match.by_id(server, game)
        participants = []
        headers = get_head(games_rank_inf)

        #We extract the information from the games and organize the data according to their participants
        for data in games_rank_inf:
            if data == 'info':
                for dat in games_rank_inf[data]:
                    if dat == 'participants':
                        for row in games_rank_inf[data][dat]:
                            participants_row = {}
                            for head in headers:
                                participants_row[head] = row[head]
                            participants.append(participants_row)
                        df = pd.DataFrame(participants)
        data_games.append(df)

    return data_games

def save_data_csv(data_games:list, user:str) -> bool:
    try:
        root = os.path.abspath(os.getcwd())
        if not os.path.isdir(root+"/files"):
            os.makedirs(root+"/files", exist_ok=True)

        for game in range(len(data_games)):
            name = root+"/files/"+ user +" "+str(game+1)+".csv"
            data_games[game].to_csv(name, index=False)
        return True

    except:
        return False

def main ():
    #Token provided by the company
    token ='RGAPI-5e2e0101-eb12-4ec2-98c7-f90ea63e8fd4'
    #User to analyze
    user= 'CNoctisx'
    #Server/Region playing
    region = 'las'
    #Date from which you want to analyze until the end date
    date = ['2022/6/1', '2022/9/8']
    #Extraction of the keywords to manage the API according to your region
    data_server = name_server(region)
    #List of games that meet the criteria
    list_games_rank= pick_games(token, user, data_server, date)
    #Data on the games that met the criteria
    data_games = game_data(token,data_server,list_games_rank)
    #Save the data in csv
    save_data_csv(data_games, user)

    #End of timer
    stop_time= (time.time() - start_time)
    print("Tiempo de ejecucion:", stop_time)

if __name__ == '__main__':
    main()