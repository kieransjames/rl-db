import requests
import time
import json
import pandas as pd

# load API token (which was not free)
token_json = json.load(open('rl_api_token.txt', 'r'))
token = token_json['token']

def get_basic_player_stats(game_code,register_frame):

    print(game_code)
    download_url = "https://ballchasing.com/api/replays/{id}".format(id=game_code)
    
    attempts=0
    while True:
        attempts = attempts+1
        if attempts>5:
            raise Exception
        try:
            response = requests.get(download_url,headers={'Authorization':token})
            break
        except TimeoutError:
            print("Timeout error, giving it a sec...")
            time.sleep(10)
            continue
        
    game_json = json.loads(response.content)

    if 'error' in game_json.keys():
        if game_json['error']=="not found":
            return None


    if len(game_json['blue']['players'])!=3 or len(game_json['orange']['players'])!=3:
        print("Teams mis-assigned...")
        return None

    orange_team = str(list(register_frame[register_frame['ballchasing_id']==game_code]['orange_team'])[0])
    blue_team = str(list(register_frame[register_frame['ballchasing_id']==game_code]['blue_team'])[0])


    if 'name' not in game_json['orange']['players'][0]:
        game_json['orange']['players'][0]['name'] = None
    if 'name' not in game_json['orange']['players'][1]:
        game_json['orange']['players'][1]['name'] = None
    if 'name' not in game_json['orange']['players'][2]:
        game_json['orange']['players'][2]['name'] = None

    if 'name' not in game_json['blue']['players'][0]:
        game_json['blue']['players'][0]['name'] = None
    if 'name' not in game_json['blue']['players'][1]:
        game_json['blue']['players'][1]['name'] = None
    if 'name' not in game_json['blue']['players'][2]:
        game_json['blue']['players'][2]['name'] = None

    # orange
    orange_1 = {"Player Name":game_json['orange']['players'][0]["name"],
                "Color":"Orange",
                "Team Name":orange_team,
                "Platform":game_json['orange']['players'][0]['id']['platform'],
                "Id":game_json['orange']['players'][0]['id']['id'],
                "Opponent Team":blue_team,
                "Date":game_json['date'],
                "Game_id":game_json['id'],
                "Game Duration":game_json['duration']}
    orange_1.update(game_json['orange']['players'][0]['stats']['core'])
    orange_1.update(game_json['orange']['players'][0]['stats']['boost'])
    orange_1.update(game_json['orange']['players'][0]['stats']['movement'])
    orange_1.update(game_json['orange']['players'][0]['stats']['positioning'])
    orange_1.update(game_json['orange']['players'][0]['stats']['demo'])

    orange_2 = {"Player Name":game_json['orange']['players'][1]["name"],
            "Color":"Orange",
            "Team Name":orange_team,
            "Platform":game_json['orange']['players'][1]['id']['platform'],
            "Id":game_json['orange']['players'][1]['id']['id'],
                "Opponent Team":blue_team,
                "Date":game_json['date'],
                "Game_id":game_json['id'],
                "Game Duration":game_json['duration']}
    orange_2.update(game_json['orange']['players'][1]['stats']['core'])
    orange_2.update(game_json['orange']['players'][1]['stats']['boost'])
    orange_2.update(game_json['orange']['players'][1]['stats']['movement'])
    orange_2.update(game_json['orange']['players'][1]['stats']['positioning'])
    orange_2.update(game_json['orange']['players'][1]['stats']['demo'])

    orange_3 = {"Player Name":game_json['orange']['players'][2]["name"],
            "Color":"Orange",
            "Team Name":orange_team,
            "Platform":game_json['orange']['players'][2]['id']['platform'],
            "Id":game_json['orange']['players'][2]['id']['id'],
                "Opponent Team":blue_team,
                "Date":game_json['date'],
                "Game_id":game_json['id'],
                "Game Duration":game_json['duration']}
    orange_3.update(game_json['orange']['players'][2]['stats']['core'])
    orange_3.update(game_json['orange']['players'][2]['stats']['boost'])
    orange_3.update(game_json['orange']['players'][2]['stats']['movement'])
    orange_3.update(game_json['orange']['players'][2]['stats']['positioning'])
    orange_3.update(game_json['orange']['players'][2]['stats']['demo'])      

    blue_1 = {"Player Name":game_json['blue']['players'][0]["name"],
            "Color":"Blue",
            "Team Name":blue_team,
            "Platform":game_json['blue']['players'][0]['id']['platform'],
            "Id":game_json['blue']['players'][0]['id']['id'],
                "Opponent Team":orange_team,
                "Date":game_json['date'],
                "Game_id":game_json['id'],
                "Game Duration":game_json['duration']}
    blue_1.update(game_json['blue']['players'][0]['stats']['core'])
    blue_1.update(game_json['blue']['players'][0]['stats']['boost'])
    blue_1.update(game_json['blue']['players'][0]['stats']['movement'])
    blue_1.update(game_json['blue']['players'][0]['stats']['positioning'])
    blue_1.update(game_json['blue']['players'][0]['stats']['demo'])  


    blue_2 = {"Player Name":game_json['blue']['players'][1]["name"],
            "Color":"Blue",
            "Team Name":blue_team,
            "Platform":game_json['blue']['players'][1]['id']['platform'],
            "Id":game_json['blue']['players'][1]['id']['id'],
                "Opponent Team":orange_team,
                "Date":game_json['date'],
                "Game_id":game_json['id'],
                "Game Duration":game_json['duration']}
    blue_2.update(game_json['blue']['players'][1]['stats']['core'])
    blue_2.update(game_json['blue']['players'][1]['stats']['boost'])
    blue_2.update(game_json['blue']['players'][1]['stats']['movement'])
    blue_2.update(game_json['blue']['players'][1]['stats']['positioning'])
    blue_2.update(game_json['blue']['players'][1]['stats']['demo'])

    blue_3 = {"Player Name":game_json['blue']['players'][2]["name"],
            "Color":"Blue",
            "Team Name":blue_team,
            "Platform":game_json['blue']['players'][2]['id']['platform'],
            "Id":game_json['blue']['players'][2]['id']['id'],
                "Opponent Team":orange_team,
                "Date":game_json['date'],
                "Game_id":game_json['id'],
                "Game Duration":game_json['duration']}
    blue_3.update(game_json['blue']['players'][2]['stats']['core'])
    blue_3.update(game_json['blue']['players'][2]['stats']['boost'])
    blue_3.update(game_json['blue']['players'][2]['stats']['movement'])
    blue_3.update(game_json['blue']['players'][2]['stats']['positioning'])
    blue_3.update(game_json['blue']['players'][2]['stats']['demo'])     

    orange_1_frame = pd.DataFrame(orange_1,index=[0])
    orange_2_frame = pd.DataFrame(orange_2,index=[0])
    orange_3_frame = pd.DataFrame(orange_3,index=[0])
    blue_1_frame = pd.DataFrame(blue_1,index=[0])
    blue_2_frame = pd.DataFrame(blue_2,index=[0])
    blue_3_frame = pd.DataFrame(blue_3,index=[0])

    return pd.concat([orange_1_frame,orange_2_frame,orange_3_frame,blue_1_frame,blue_2_frame,blue_3_frame])

        
# given a csv of replay ids, returns pandas dataframe of stats for all games
def add_player_game_stats(register_df):
   
    list_of_games = list(register_df['ballchasing_id'])

    new_games_df = [get_basic_player_stats(game,register_df) for game in list_of_games]
    new_games_df = pd.concat(new_games_df,axis=0)
    return new_games_df

