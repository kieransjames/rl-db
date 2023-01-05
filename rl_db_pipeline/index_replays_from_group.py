# contains all functions necessary to generate a csv file with all the replay_ids of a given group on ballchasing.com 

import urllib.request as ur
import re
import pandas as pd
import requests
import time
import json

# load API token (which was not free)
token_json = json.load(open('rl_api_token.txt', 'r'))
token = token_json['token']


class NoGamesTodayException(Exception):
    pass

def add_replay_ids_to_list(file_path,url):
    
    
    import urllib.request as ur
    import re
    import pandas as pd
    import time


    def grep_index(lines, pattern):
        indices = [index for index in list(range(0, len(lines))) if re.search(pattern,str(lines[index])) is not None]
        return (indices)

    after = ""

    while True:
        try:
            response = ur.urlopen(url+after)
            break
        except ur.HTTPError as e:
            if e.code == 429:
                print("Too many requests, cooling off for 5 seconds...")
                time.sleep(5)
                continue
            else:
                print("Not a 429 error...")
                raise Exception

    html = response.readlines()

    game_indices = grep_index(html,pattern="data-id=\"(.*)\"")

    ballchasing_id = [""]*len(game_indices)
    unique_id = [""]*len(game_indices)
    date = [""]*len(game_indices)
    rank = [""]*len(game_indices)


    count=0
    for index in game_indices:
        ballchasing_id[count] = re.search(r"data-id=\"(.*)\"", str(html[index])).group(1)    
        count=count+1


    date_indices = grep_index(html,pattern="<div title=\"When the game took place\">(.*)</div>")
    count=0
    for index in date_indices:
        date[count] = re.search(r"<div title=\"When the game took place\">(.*)</div>", str(html[index])).group(1)
        count+=1

    blue_team = []
    orange_team = []

    try:
        blue_team_index = grep_index(html,pattern='<div class=\"blue team\">')
        orange_team_index = grep_index(html,pattern='<div class=\"orange team\">')

        if len(blue_team_index) is not len(orange_team_index):
            print("can't find all teams")
            raise Exception

        for index in blue_team_index:
            blue_team.append(str(html[index+2]).split("\"team-name\">")[1].split("</div>")[0])
        for index in orange_team_index:
            orange_team.append(str(html[index+2]).split("\"team-name\">")[1].split("</div>")[0])
    except:
        print("oop")
        raise Exception


    pd_dic = {
        "ballchasing_id":ballchasing_id,
        "replay_date":date,
        "group":[url]*len(ballchasing_id),
        "blue_team":blue_team,
        "orange_team":orange_team
    }

    new_downloaded_games_register = pd.DataFrame(pd_dic)

    try:
        old_downloaded_games_register = pd.read_csv(file_path,index_col=False)
    except FileNotFoundError:
        old_downloaded_games_register = new_downloaded_games_register[0:1]

    updated_downloaded_games_register = pd.concat([old_downloaded_games_register,new_downloaded_games_register])\
        .drop_duplicates(subset=["ballchasing_id"])

    updated_downloaded_games_register.to_csv(file_path,index=False)

    
    return None


# given the url for a replay group that has sub-groups, return all sub-groups
def get_sub_groups(url):
    
    print(url)

    while True:
      try:
        response = ur.urlopen(url)
        break
      except Exception as e:
        if isinstance(e,ur.HTTPError) and e.code == 429:
            print("Too many requests, cooling off for 5 seconds...")
            time.sleep(5)
            continue
        else:
          print("Not a 429 error...")
          return None
        

    def grep_index(lines, pattern):
       indices = [index for index in list(range(0, len(lines))) if re.search(pattern,str(lines[index])) is not None]
       return (indices)

    html = response.readlines()
    results_index = grep_index(html, pattern="<a href=\"/group/")


    groups = []
    for index in results_index:
      if "</h2>" in str(html[index+1]):
         groups.append("https://ballchasing.com/group/"+re.search(r"<a href=\"/group/([^']*)\">", str(html[index])).group(1))
    return groups

# given a url for a replay group (either a parent replay group or granular), append all replay metadata to specified csv
# recursively searches through all subgroups until it finds the granular replays, and then adds them
def index_group(url, output_file_path):

    sub_groups = get_sub_groups(url)
    print(sub_groups)

    if sub_groups is None:
        return None

    if len(sub_groups)==0:
        try:
            add_replay_ids_to_list(output_file_path,url)
            return []
        except:
            print("Empty group...")
            pass
    else:
        for sub_group in sub_groups:
            index_group(sub_group,output_file_path=output_file_path)
