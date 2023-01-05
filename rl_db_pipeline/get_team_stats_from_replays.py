import requests
import time
import json
import pandas as pd

# load API token (which was not free)
token_json = json.load(open('rl_api_token.txt', 'r'))
token = token_json['token']


# given a game code, and a csv of game meta data, retrieves team stats from ballchasing API
def get_basic_team_stats(game_code,register_frame):

    print(game_code)
    download_url = "https://ballchasing.com/api/replays/{id}".format(id=game_code)
    response = requests.get(download_url,headers={'Authorization':token})
    game_json = json.loads(response.content)

    if 'error' in game_json.keys():
        if game_json['error']=="not found":
            return None


    
    orange_team = str(list(register_frame[register_frame['ballchasing_id']==game_code]['orange_team'])[0])
    blue_team = str(list(register_frame[register_frame['ballchasing_id']==game_code]['blue_team'])[0])
    orange_dic = {"Name":orange_team,"Opponent":blue_team}
    blue_dic = {"Name":blue_team,"Opponent":orange_team}

    try:
        if orange_team.isna():
            try:
                print("Getting orange name from API...")
                orange_team = str(game_json["orange"]["name"])
            except:
                print("Couldn't get an orange name...")
                pass
        if blue_team.isna():
            try:
                print("Getting blue name from API...")
                blue_team = str(game_json["blue"]["name"])
            except:
                print("Couldn't get a blue name...")
                pass
    except:
        pass

    orange_dic.update({
        "Color":"Orange",
        "Opponent Color":"Blue",
        "Date":game_json['date'],
        "Game_id":game_json['id'],
        "Game Duration":game_json['duration']})    
    orange_dic.update(game_json["orange"]['stats']['ball'])
    orange_dic.update(game_json["orange"]['stats']['core'])
    orange_dic.update(game_json["orange"]['stats']['boost'])
    orange_dic.update(game_json["orange"]['stats']['movement'])
    orange_dic.update(game_json["orange"]['stats']['positioning'])
    orange_dic.update(game_json["orange"]['stats']['demo'])


    blue_dic.update({
        "Color":"Blue",
        "Opponent Color":"Orange",
        "Date":game_json['date'],
        "Game_id":game_json['id'],
        "Game Duration":game_json['duration']})
    blue_dic.update(game_json["blue"]['stats']['ball'])
    blue_dic.update(game_json["blue"]['stats']['core'])
    blue_dic.update(game_json["blue"]['stats']['boost'])
    blue_dic.update(game_json["blue"]['stats']['movement'])
    blue_dic.update(game_json["blue"]['stats']['positioning'])
    blue_dic.update(game_json["blue"]['stats']['demo'])

    team_stats_df = pd.DataFrame([orange_dic,blue_dic])

    return team_stats_df

# given a csv of replay ids, returns pandas dataframe of stats for all games
def add_team_game_stats(register_df):
   
    list_of_games = list(register_df['ballchasing_id'])

    new_games_df = [get_basic_team_stats(game,register_df) for game in list_of_games]
    new_games_df = pd.concat(new_games_df,axis=0)
    return new_games_df
