# much of the logic of this program is the same as 1_Team_Stats.py

import streamlit as st
st.set_page_config(layout="wide",
                   page_title="RL-DB: Player Stats",
                   page_icon=":video_game:",
                   menu_items={
                    "Report a Bug":None,
                    "Get help":None,
                    "About":None
                   })

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)


css = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''
st.markdown(css, unsafe_allow_html=True)


import pandas as pd
import pandas.api.types
import numpy as np
import mysql.connector
from mysql.connector import Error
import datetime
import json
from st_aggrid import AgGrid, GridOptionsBuilder

import os 
if "/rl_db_app/pages" not in os.getcwd():
    os.chdir('./rl_db_app/pages')

with open('Event_dic.txt') as f:
    data = f.read()
event_dates = json.loads(data)


def get_event_type(date_str,region,event_dic):

    if region not in ["APAC","EU","MENA","NA","OCE","SAM","SSA"]:
        return ("INVALID","INVALID","INVALID")

    temp_dic = event_dic[region]

    date_str = date_str.split("T")[0]

    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

    if date >= datetime.datetime(year=2022, month=9, day=1) and date <= datetime.datetime(year=2022, month=12, day=31):
        split="Fall"
    elif date >= datetime.datetime(year=2023, month=1, day=1) and date <= datetime.datetime(year=2023, month=4, day=15):
        split="Winter"
    elif date >= datetime.datetime(year=2023, month=4, day=16) and date <= datetime.datetime(year=2023, month=7, day=15):
        split="Spring"
    else:
        try:
            start_date = datetime.datetime.strptime(event_dic["Majors"]["Worlds"]["start"], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(event_dic["Majors"]["Worlds"]["end"], '%Y-%m-%d')
            if date >=start_date and date<=end_date:
                return ("Worlds","Major","Main Event")
            else:
                return ("INVALID","INVALID","INVALID")
        except:
            pass
        


    temp_dic = temp_dic[split]

    for event in temp_dic:
        for sub_event in temp_dic[event]:
            try:
                start_date = datetime.datetime.strptime(temp_dic[event][sub_event]["start"], '%Y-%m-%d')
                end_date = datetime.datetime.strptime(temp_dic[event][sub_event]["end"], '%Y-%m-%d')
                if date >=start_date and date<=end_date:
                    return (split,"Regional",sub_event)
            except:
                pass

    for split in event_dic["Majors"]:
        try:
            start_date = datetime.datetime.strptime(event_dic["Majors"][split]["Main Event"]["start"], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(event_dic["Majors"][split]["Main Event"]["end"], '%Y-%m-%d')
            if date >=start_date and date<=end_date:
                return (split,"Major","Main Event")
        except:
            pass
           
    return ("INVALID","INVALID","INVALID")

# load API token (which was not free)
json_credentials = json.load(open('rl_db_credentials.txt', 'r'))
user_name = json_credentials['user_name']
db_address = json_credentials['db_address']
db_name = json_credentials['db_name']
password = json_credentials['password']

# Connect to MySQL database

@st.cache(show_spinner=False)
def init_app():
    try:
        conn = mysql.connector.connect(host=db_address,
                                        database=db_name,
                                        user=user_name,
                                        password=password)

        my_cursor=conn.cursor()
        
# team_bios
        query = "SELECT * FROM team_bios"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_bios = pd.read_sql(query, conn)


# team_aliases
        query = "SELECT * FROM team_aliases"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_aliases = pd.read_sql(query, conn)

# player_ids
        query = "SELECT * FROM player_ids"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        player_ids = pd.read_sql(query, conn)

# player_meta_register
        query = "SELECT * FROM player_meta_register"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()

        player_meta_register = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").\
        drop(["team_alias"],axis=1).\
        merge(team_aliases,left_on="opponent_alias",right_on="team_alias",how="left").\
        rename(columns={"team_name_y":"opponent_team_name","team_name_x":"team_name"}).\
        drop(["opponent_alias"],axis=1).\
        merge(team_bios[["team_name","region"]],on="team_name",how="left").\
        rename(columns={"region":"team_region"}).\
        merge(player_ids,on="player_id",how="left").\
        drop(["platform_x","team_alias"],axis=1).\
        rename(columns={"platform_y":"platform"}).\
        merge(team_bios[["team_name","region"]],left_on="opponent_team_name",right_on="team_name",how="left").\
        rename(columns={"region":"opponent_region","team_name_x":"team_name"}).\
        drop(["team_name_y"],axis=1)


        event_tuples = [get_event_type(str(date_),region_,event_dates) for date_,region_ in zip(player_meta_register.game_date,player_meta_register.team_region)]

        splits = [tup[0] for tup in event_tuples]
        event_type = [tup[1] for tup in event_tuples]
        event_sub_type = [tup[2] for tup in event_tuples]

        player_meta_register["Split"] = splits
        player_meta_register["Event Type"] = event_type
        player_meta_register["Event Sub-type"] = event_sub_type

        player_meta_register = player_meta_register[["player_id","player_name","game_id","platform","team_name","opponent_team_name","color",
                                                     "game_date","team_region","opponent_region","Split","Event Type","Event Sub-type"]]



# player_base_stats
        query = "SELECT * FROM player_base_stats"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        player_base_stats = pd.read_sql(query, conn).merge(player_ids,on="player_id",how="left")
        player_base_stats.columns = player_base_stats.columns.str.replace('_',' ').str.title()
        player_base_stats = player_base_stats.drop(["Shooting Percentage","Platform"],axis=1)

# player_boost_stats
        query = "SELECT * FROM player_boost_stats"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        player_boost_stats = pd.read_sql(query, conn).merge(player_ids,on="player_id",how="left")
        player_boost_stats.columns = player_boost_stats.columns.str.replace('_',' ').str.title()

# player_movement_stats
        query = "SELECT * FROM player_movement_stats"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        player_movement_stats = pd.read_sql(query, conn).merge(player_ids,on="player_id",how="left")
        player_movement_stats.columns = player_movement_stats.columns.str.replace('_',' ').str.title()

# player_positioning_stats
        query = "SELECT * FROM player_positioning_stats"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        player_positioning_stats = pd.read_sql(query, conn).merge(player_ids,on="player_id",how="left")
        player_positioning_stats.columns = player_positioning_stats.columns.str.replace('_',' ').str.title()

# player_demo_stats
        query = "SELECT * FROM player_demo_stats"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        player_demo_stats = pd.read_sql(query, conn).merge(player_ids,on="player_id",how="left")
        player_demo_stats.columns = player_demo_stats.columns.str.replace('_',' ').str.title()

# rename columns
        player_meta_register = player_meta_register.rename(columns={
            "player_name":"Player Name",
            "team_name":"Team Name",
            "player_id":"Player Id",
            "game_id":"Game Id",
            "platform":"Platform",
        })

        return {
            'player_ids':player_ids,
            'player_meta_register':player_meta_register,
            'player_base_stats':player_base_stats,
            'player_boost_stats':player_boost_stats,
            'player_movement_stats':player_movement_stats,
            'player_positioning_stats':player_positioning_stats,
            'player_demo_stats':player_demo_stats
        }
        
        
    except Error as e:
        print(e)
    	
with st.spinner('Connecting to database, standby...'):
    dfs = init_app()

player_meta_register = dfs['player_meta_register']
player_base_stats = dfs['player_base_stats']
player_boost_stats = dfs['player_boost_stats']
player_movement_stats = dfs['player_movement_stats']
player_positioning_stats = dfs['player_positioning_stats']
player_demo_stats = dfs['player_demo_stats']


# list of players and teams
players = sorted(list(player_meta_register['Player Name'].unique()))
teams = sorted([str(x) for x in player_meta_register['Team Name'].unique()])

def aggregate_df(df,columns,per_game=True):
    temp1 = df.copy(deep=True)
    counts = temp1.groupby(["Player Name","Player Id"],as_index=False)["Player Name"].count().rename(columns={"Player Name":"GP"})
    if per_game:
        temp2 = temp1.groupby(["Player Name","Player Id"],as_index=False)[columns].mean().drop(["Player Id"],axis=1)
    else:
        temp2 = temp1.groupby(["Player Name","Player Id"],as_index=False)[columns].sum().drop(["Player Id"],axis=1)        
    temp3 = pd.concat([counts,temp2],axis=1)
    new_cols = list(temp3.columns)
    temp4 = temp3[["Player Name"]+[x for x in new_cols if x!='Player Name']]
    return temp4



@st.cache(show_spinner=True)
def default_table():
    display_df = player_meta_register.merge(player_base_stats,on=["Player Id","Game Id"],how="left").drop(["Game Id","opponent_team_name","color","Platform","Team Name",
                                                                                                       "game_date","team_region","opponent_region","Split",
                                                                                                       "Event Type","Event Sub-type","Player Name_y"],axis=1).\
                                                                                                    rename(columns={"Player Name_x":"Player Name"})
    return aggregate_df(display_df,list(display_df.columns),True)

def custom_round_0(x):
    if pandas.api.types.is_numeric_dtype(x):
        return round(x)
    else:
        return x
def custom_round_1(x):
    if x.name=="GP":
        return round(x,1)
    if pandas.api.types.is_numeric_dtype(x):
        return round(x,1)
    else:
        return x


st.title('Player Stats')
st.subheader("Below are the up-to-date cumulative statistics for the RLCS 2022-2023 season, by player. Submit a query using the filters below for more specific stats.")


default_df = default_table()

col1_header, col2_header, col3_header, col4_header = st.columns(4)

with col4_header:
    date_check = st.checkbox('Filter by date')

with st.form("my_form"):
    st.write("Select parameters:")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        Split = st.multiselect(
            'Split',
            ["Fall","Winter","Spring","Worlds"],
            []
        )

        Event_type = st.multiselect(
            'Event Type',
            ["Major","Regional"],
            []
        )

        Event_sub_type = st.multiselect(
            'Event Sub-Type',
            ["Main Event","Qualifier"],
            []
        )


    with col2:
        teams_for = st.multiselect(
            'Team',
            teams,
            []
        )
        Region = st.multiselect(
            'Region',
            ["APAC","EU","MENA","NA","OCE","SAM","SSA"],
            []
        )

        per_game = st.radio(
        "hidden",
        ('Per game stats', 'Total stats'),
        horizontal=True,label_visibility="hidden")

        if per_game=='Per game stats':
            per_game_bool = True
        else:
            per_game_bool = False

    with col3:
        teams_against = st.multiselect(
            'Opposing team',
            teams,
            []
        )
        Opponent_region = st.multiselect(
            'Opponent Region',
            ["APAC","EU","MENA","NA","OCE","SAM","SSA"],
            []
        )

        players_for = st.multiselect(
            'Player',
            players,
            []
        )


    with col4:
        if date_check:
            start_date = st.date_input(
                "As of:",
                datetime.date(2022,9,1)
            )
            end_date = st.date_input(
                "Up to:",
                datetime.date(2023,1,1)
            )


    Stats_select = st.multiselect(
            'Statistical categories:',
            ["Base stats","Demos","Boost stats","Movement","Positioning"],
            []
        )

    temp_df = player_meta_register

    max_GP = int(default_df['GP'].max())

    min_gp = st.slider(
        "Minimum Games Played:",
        0,max_GP, (0,max_GP)
        )

    submitted = st.form_submit_button("Submit query")
    if submitted:
    
        # filter by split:
        if len(Split)!=0:
            temp_df = temp_df[temp_df["Split"].isin(Split)]
        # filter by event:
        if len(Event_type)!=0:
            temp_df = temp_df[temp_df["Event Type"].isin(Event_type)]
        # filter by sub-event type:
        if len(Event_sub_type)!=0:
            temp_df = temp_df[temp_df["Event Sub-type"].isin(Event_sub_type)]
        
        # filter by team:
        if len(teams_for)!=0:
            temp_df = temp_df[temp_df["Team Name"].isin(teams_for)]
        # filter by player 
        if len(players_for)!=0:
            temp_df = temp_df[temp_df["Player Name"].isin(players_for)]
        # filter by region:
        if len(Region)!=0:
            temp_df = temp_df[temp_df["team_region"].isin(Region)]

        # filter by opposiong team:
        if len(teams_against)!=0:
            temp_df = temp_df[temp_df["opponent_team_name"].isin(teams_against)]
        # filter by opponent region:
        if len(Opponent_region)!=0:
            temp_df = temp_df[temp_df["opponent_region"].isin(Opponent_region)]

# filter by date:
        if date_check:
            temp_df = temp_df[(temp_df["game_date"]>=start_date) & (temp_df["game_date"]<=end_date)]


        stats_cats_dic = {
            "Base stats":player_base_stats,
            "Demos":player_demo_stats,
            "Boost stats":player_boost_stats,
            "Movement":player_movement_stats,
            "Positioning":player_positioning_stats
        }

    
        
    


# merge with requested stat categories
        if len(Stats_select)==0:
            temp_df = temp_df.merge(player_base_stats,on=["Player Id","Game Id"],how="left").drop(["Game Id","opponent_team_name","color","Platform",
                                                                                                       "game_date","team_region","opponent_region","Split",
                                                                                                       "Event Type","Event Sub-type","Player Name_y"],axis=1).\
                                                                                                    rename(columns={"Player Name_x":"Player Name"})
        else:
            for stats_cat in Stats_select:
                temp_df = temp_df.merge(stats_cats_dic[stats_cat],on=["Player Id","Game Id"],how="left").rename(columns={"Player Name_x":"Player Name",
                                                                                                                         "Platform_x":"Platform"})
            temp_df = temp_df.drop(["Game Id","Player Id","opponent_team_name","color","Platform","game_date","team_region","opponent_region","Split","Event Type","Event Sub-type","Player Name_y"],axis=1)

        
        display_df = aggregate_df(temp_df,list(temp_df.columns),per_game_bool)

        if per_game_bool:
            display_df = display_df.apply(custom_round_1)
        else:
            display_df = display_df.apply(custom_round_0)
        
        display_df = display_df[(display_df['GP']>=min_gp[0]) & (display_df['GP']<=min_gp[1])]

    if not submitted:
        display_df = default_df
        display_df = display_df.apply(custom_round_1)


from st_aggrid import AgGrid, GridOptionsBuilder
gb = GridOptionsBuilder.from_dataframe(display_df)

base_width = 67
width_factor = 5

for col in list(display_df.columns):

    col_len = len(col)

    if col == "Player Name":
        gb.configure_column(col, precision=1, width=170,pinned="left")
    elif col == "Team Name":
        gb.configure_column(col, precision=1, width=190)
    elif col == "Platform":
        gb.configure_column(col, precision=1, width=90)
    elif col == "GP":
        gb.configure_column(col, precision=1, width=60)
    else:
        gb.configure_column(col, precision=1, width=(col_len*width_factor+base_width))



AgGrid(display_df, gridOptions=gb.build(),height=800,update_mode="NO_UPDATE")
