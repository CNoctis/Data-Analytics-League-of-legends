import os
import time
import pathlib
import datetime
import pandas as pd
import logging.config
import logging.handlers
from riotwatcher import LolWatcher
from userdata import UserData


#cfg file path for log
log_file_path = str(pathlib.Path().absolute()) + "/config/config_log.cfg"

#logging config
logging.config.fileConfig(log_file_path)

#logger
logger = logging.getLogger('root')

#Start of timer
start_time = time.time()

def current_date() -> str:
    """
    Get the current date
    return: day
    """
    #current date
    now = datetime.datetime.now()
    
    #date in year, month, day format
    day = now.strftime("%Y/%m/%d")
    return day


def get_head(games_rank_inf:dict) -> list:
    """
    Returns the keywords/headings of each column
    """
    try:
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
    except:
        logger.info("Error getting headers")


def date_conversion(date:list) -> list:
    """
    Convert date string to epoch time
    date: list date
    retrun: date list int epoch format, [start, end]
    """ 
    try:
        format = '%Y/%m/%d'
        date_ini = date[0]
        date_fn = date[1]
        epoch = datetime.datetime(1970, 1, 1)
        epoch_ini = int ((datetime.datetime.strptime(date_ini, format) - epoch).total_seconds())
        epoch_fn = int ((datetime.datetime.strptime(date_fn, format) - epoch).total_seconds())
        logger.info('Successful date conversion')
        return [epoch_ini, epoch_fn]
    except:
        logger.info('Date conversion error')

def name_server(region:str) -> list:
    """
    Provide the server name and region for the correct use of the API
    region: user region
    return: List with server name and region
    """
    try:
        region = region.upper()
        servers = {
                'BR':['BR1', 'AMERICAS'], 'NA':['NA1','AMERICAS'], 'LAN':['LA1', 'AMERICAS'], 'LAS':['LA2', 'AMERICAS'],
                'KR':['KR', 'ASIA '], 'JP': ['JP1', 'ASIA'],
                'EUN':['EUN1', 'EUROPE '], 'EUW':['EUW1', 'EUROPE'], 'TR':['TR1', 'EUROPE'], 'RU':['RU', 'EUROPE'],
                'OCE':['OC1','SEA']
                }
        for server in servers:
            if server == region:
                logger.info('Server obtained successfully')
                return servers[server]
            else:
                pass
    except:
        logger.info('Failed to get server')

def player_data(token:str, user:str, data_server:list, date:list) -> list:
    """
    Extract the game list.
    Extract player information in solo/q.

    token: Code provided by riot developer
    user: Username
    data_server: list with region and server
    date: start and end date
    return: [game lists, p_data]
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
        logger.info('Successful matchmaking')

        p_data = lol_watcher.league.by_summoner(region, usuario['id'])
        #p_data[0] = solo/q --- p_data[1] = flex
        return [list_games_rank, [p_data[0]]]
    except:
        logger.info('Get failed matches, verify token, user and region')


def game_data(token:str, data_server:list, list_games_rank:list, p_data:dict) -> list:
    """
    Extract all the information of the game and info 

    token: Code provided by riot developer
    data_server: list with region and server
    list_games_rank: List of games played by the player
    p_data: Player information in solo/q
    return: [game data list, player data]
    """
     #token:  Token provided by the company
            #20 requests every 1 second(s)
            #100 requests every 2 minute(s)

    #API connection

    try:
        lol_watcher = LolWatcher(token)
        server = data_server[1]
        #Player information solo/q
        player = pd.DataFrame(p_data)
        logger.info('User data saved successfully')

        #Data the game
        data_games=[]
        for game in list_games_rank:
            #Ranker games information
            games_rank_inf = lol_watcher.match.by_id(server, game)
            participants = []
            headers = get_head(games_rank_inf)
            i = 0
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
                            i+= 1
            data_games.append(df)

        logger.info('Successfully saved games')
        return [data_games, player]

    except:
        logger.info('Failed to save data')

def save_data_csv(data_games:list, user:str) -> bool:
    """
    Save all the information of the games and the user in csv format

    data_games: [game information, player information]
    user: Username
    return: bool
    """

    try:
        #root directory
        root = os.path.abspath(os.getcwd())
        if not os.path.isdir(root+"/files"):
            os.makedirs(root+"/files", exist_ok=True)
        #save games
        for game in range(len(data_games[0])):
            #path, name and format in which the information of the games was saved
            name = root+"/files/"+ user +" "+str(game+1)+".csv"
            #data_games[0] = game data list / data_games[1] = player data
            data_games[0][game].to_csv(name, index=False)
        logger.info('Successful CSV file creation')

        #path, name and format in which the player information was saved
        name_p = root+"/files/"+ "Game"+ user +".csv"
        #data_games[0] = game data list / data_games[1] = player data
        data_games[1].to_csv(name_p, index=False)

        return True
    except:
        logger.info('Failed to create CSV files')
        return False

def user_data():
    user_dt = UserData('xxx.xxxx', 'CNoctisx', 'LAS', '2022/06/01')
    return user_dt


def main ():
    #User data
    user_d = user_data()
    #get current date
    day = current_date()
    #Date from which you want to analyze until the end date
    date = [user_d.date_ini, day]
    #Extraction of the keywords to manage the API according to your region
    data_server = name_server(user_d.region)
    #Game list and information
    data_player = player_data(user_d.token, user_d.user, data_server, date)
    #Game list
    list_games_rank= data_player[0]
    #player data
    p_data = data_player[1]
    #Data on the games that met the criteria
    data_games = game_data(user_d.token ,data_server ,list_games_rank ,p_data)
    #Save the data in csv
    save_data_csv(data_games, user_d.user)

    #End of timer
    stop_time= (time.time() - start_time)
    print("Tiempo de ejecucion:", stop_time)

if __name__ == '__main__':
    main()