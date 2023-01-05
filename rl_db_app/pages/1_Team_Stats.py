import streamlit as st

# configure page to wide layout, set title & icon
st.set_page_config(layout="wide",
                   page_title="RL-DB: Team Stats",
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


# remove border around submit container
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


# make sure we're in the right directory to find 'Event_dic.txt'
import os 
if "/rl_db_app/pages" not in os.getcwd():
    os.chdir('./rl_db_app/pages')

# load json with dates for each event, in order to classify which split a game was played in, whether it's a regional or major, whether it's a qualifier or main event
with open('Event_dic.txt') as f:
    data = f.read()
event_dates = json.loads(data)

# use json 'event_dates' to get split and event types
def get_event_type(date_str,region,event_dic):

#   check for invalid region
    if region not in ["APAC","EU","MENA","NA","OCE","SAM","SSA"]:
        return ("INVALID","INVALID","INVALID")

#   narrow our search to the given region
    temp_dic = event_dic[region]

# get year-month-date as a string
    date_str = date_str.split("T")[0]
# convert to datetime
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

#   assign split
    if date >= datetime.datetime(year=2022, month=9, day=1) and date <= datetime.datetime(year=2022, month=12, day=31):
        split="Fall"
    elif date >= datetime.datetime(year=2023, month=1, day=1) and date <= datetime.datetime(year=2023, month=4, day=15):
        split="Winter"
    elif date >= datetime.datetime(year=2023, month=4, day=16) and date <= datetime.datetime(year=2023, month=7, day=15):
        split="Spring"
# check if we're actually at worlds 
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
        

# narrow our search down to which split we're in
    temp_dic = temp_dic[split]

#  iterate through events in the split to find event
    for event in temp_dic:
        for sub_event in temp_dic[event]:
            try:
                start_date = datetime.datetime.strptime(temp_dic[event][sub_event]["start"], '%Y-%m-%d')
                end_date = datetime.datetime.strptime(temp_dic[event][sub_event]["end"], '%Y-%m-%d')
                if date >=start_date and date<=end_date:
                    return (split,"Regional",sub_event)
            except:
                pass
              
# check the major separately, since majors don't technically have a region 
    for split in event_dic["Majors"]:
        try:
            start_date = datetime.datetime.strptime(event_dic["Majors"][split]["Main Event"]["start"], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(event_dic["Majors"][split]["Main Event"]["end"], '%Y-%m-%d')
            if date >=start_date and date<=end_date:
                return (split,"Major","Main Event")
        except:
            pass
           
# if nothing worked, return invalid
    return ("INVALID","INVALID","INVALID")

# load API token (which was not free)
json_credentials = json.load(open('rl_db_credentials.txt', 'r'))
user_name = json_credentials['user_name']
db_address = json_credentials['db_address']
db_name = json_credentials['db_name']
password = json_credentials['password']

# Connect to MySQL database, and load relevant info
# cache results so the app doesn't bother the database for every user; instead, it will load once when the app is booted, and keep the results cached
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
    
# team_meta_register
        query = "SELECT * FROM team_meta_register"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_meta_register = pd.read_sql(query, conn)
        team_meta_register = team_meta_register.merge(team_aliases,on="team_alias",how="left").merge(team_aliases,left_on="opponent_alias",right_on="team_alias",how="left").\
            merge(team_bios[["team_name","region"]],left_on="team_name_x",right_on="team_name",how="left").drop(["team_alias_x","team_alias_y","team_name_x","opponent_alias"],axis=1)
        team_meta_register = team_meta_register.rename(columns = {
            "team_name_y":"opponent_name",
            "region":"team_region"
        }).merge(team_bios[["team_name","region"]],left_on="opponent_name",right_on="team_name",how="left").\
        rename(columns={
                "region":"opponent_region",
                "team_name_x":"team_name"
        }).drop(["team_name_y"],axis=1)
        team_meta_register["opponent_color"] = ["Blue" if color == "Orange" else "Orange" for color in team_meta_register.color]

        event_tuples = [get_event_type(str(date_),region_,event_dates) for date_,region_ in zip(team_meta_register.game_date,team_meta_register.team_region)]

        splits = [tup[0] for tup in event_tuples]
        event_type = [tup[1] for tup in event_tuples]
        event_sub_type = [tup[2] for tup in event_tuples]

        team_meta_register["Split"] = splits
        team_meta_register["Event Type"] = event_type
        team_meta_register["Event Sub-type"] = event_sub_type

        team_meta_register = team_meta_register[["game_id","team_name","opponent_name","color","opponent_color","game_date","team_region","opponent_region","Split","Event Type","Event Sub-type"]]


# team_base_stats
        query = "SELECT * FROM team_base_stats"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_base_stats = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_base_stats.columns = team_base_stats.columns.str.replace('_',' ').str.title()

# team_boost_stats_for
        query = "SELECT * FROM team_boost_stats_for"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_boost_stats_for = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_boost_stats_for.columns = team_boost_stats_for.columns.str.replace('_',' ').str.title()

# team_movement_stats_for
        query = "SELECT * FROM team_movement_stats_for"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_movement_stats_for = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_movement_stats_for.columns = team_movement_stats_for.columns.str.replace('_',' ').str.title()

# team_positioning_stats_for
        query = "SELECT * FROM team_positioning_stats_for"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_positioning_stats_for = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_positioning_stats_for.columns = team_positioning_stats_for.columns.str.replace('_',' ').str.title()

# team_demo_stats
        query = "SELECT * FROM team_demo_stats"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_demo_stats = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_demo_stats.columns = team_demo_stats.columns.str.replace('_',' ').str.title()

# team_boost_stats_against
        query = "SELECT * FROM team_boost_stats_against"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_boost_stats_against = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_boost_stats_against.columns = team_boost_stats_against.columns.str.replace('_',' ').str.title()

# team_movement_stats_against
        query = "SELECT * FROM team_movement_stats_against"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_movement_stats_against = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_movement_stats_against.columns = team_movement_stats_against.columns.str.replace('_',' ').str.title()

# team_positioning_stats_against
        query = "SELECT * FROM team_positioning_stats_against"
        my_cursor.execute(query)
        myresult = my_cursor.fetchall()
        team_positioning_stats_against = pd.read_sql(query, conn).merge(team_aliases,on="team_alias",how="left").drop(["team_alias"],axis=1)
        team_positioning_stats_against.columns = team_positioning_stats_against.columns.str.replace('_',' ').str.title()

# rename columns
        team_meta_register = team_meta_register.rename(columns={
            "team_name":"Team Name",
            "game_id":"Game Id"
        })

        team_base_stats = team_base_stats.rename(columns={
            "Against Possession Time":"Possession Time Against",
            "Against Time In Side":"Time In Side Against",
            "Against Assists":"Assists Against",
            "Against Score":"Score Against",
            "Against Saves":"Saves Against"
        })

        team_base_stats = team_base_stats[["Team Name","Game Id","Win","Goals","Assists","Saves","Shots",
                                           "Goals Against","Assists Against","Saves Against","Shots Against",
                                           "Score","Score Against",
                                           "Possession Time",
                                           "Possession Time Against",
                                           "Time In Side",
                                           "Time In Side Against",
                                           "Game Duration"]]

        return {
            "team_bios":team_bios,
            'team_aliases':team_aliases,
            'team_meta_register':team_meta_register,
            'team_base_stats':team_base_stats,
            'team_boost_stats_for':team_boost_stats_for,
            'team_movement_stats_for':team_movement_stats_for,
            'team_positioning_stats_for':team_positioning_stats_for,
            'team_demo_stats':team_demo_stats,
            'team_boost_stats_against':team_boost_stats_against,
            'team_movement_stats_against':team_movement_stats_against,
            'team_positioning_stats_against':team_positioning_stats_against
        }
        
        
    except Error as e:
        print(e)
    	
# contact the DB
with st.spinner('Connecting to database, standby...'):
    dfs = init_app()

# unpack our results from the DB
team_meta_register = dfs['team_meta_register']
team_base_stats = dfs['team_base_stats']
team_boost_stats_for = dfs['team_boost_stats_for']
team_movement_stats_for = dfs['team_movement_stats_for']
team_positioning_stats_for = dfs['team_positioning_stats_for']
team_demo_stats = dfs['team_demo_stats']
team_boost_stats_against = dfs['team_boost_stats_against']
team_movement_stats_against = dfs['team_movement_stats_against']
team_positioning_stats_against = dfs['team_positioning_stats_against']


# get list of teams
teams = sorted(list(team_meta_register['Team Name'].unique()))

# given a dataframe game by game stats, group stats by team (either summing or averaging)
def aggregate_df(df,columns,per_game=True):
    temp1 = df.copy(deep=True)
    if per_game:
        if "Win" in list(temp1.columns):
            temp1["Win%"] = temp1["Win"]*100
            temp1 = temp1.drop(["Win"],axis=1)
            columns = ["Win%" if x=="Win" else x for x in columns]
    counts = temp1.groupby(["Team Name","team_region"],as_index=False)["Team Name"].count().rename(columns={"Team Name":"GP"})
    if per_game:
        temp2 = temp1.groupby(["Team Name","team_region"],as_index=False)[columns].mean().drop(["team_region"],axis=1)
    else:
        temp2 = temp1.groupby(["Team Name","team_region"],as_index=False)[columns].sum().drop(["team_region"],axis=1)        
    temp3 = pd.concat([counts,temp2],axis=1)
    new_cols = list(temp3.columns)
    temp4 = temp3[["Team Name"]+[x for x in new_cols if x!='Team Name']].drop(["team_region"],axis=1)
    return temp4








# the 'default' table is what shows when the page initially loads, showing base stats for all teams
# we cache this because why wouldn't we
@st.cache(show_spinner=True)
def default_table():
    display_df = team_meta_register.merge(team_base_stats,on=["Team Name","Game Id"],how="left").drop(["Game Id","opponent_name","color","opponent_color",
                                                                                                       "game_date","opponent_region","Split",
                                                                                                       "Event Type","Event Sub-type"],axis=1)
    return aggregate_df(display_df,list(display_df.columns),True)

#  functions that round all numeric columns
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


st.title('Team Stats')
st.subheader("Below are the up-to-date cumulative statistics for the RLCS 2022-2023 season, by team. Submit a query using the filters below for more specific stats.")

# define four header columns
col1_header, col2_header, col3_header, col4_header = st.columns(4)

# an option to filter by date
with col4_header:
    date_check = st.checkbox('Filter by date')

# load the default table    
default_df = default_table()

# bundle our query options together as a form 
with st.form("my_form"):
    st.write("Select parameters:")
    col1, col2, col3, col4 = st.columns(4)

# filter by split and event types
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

# filter by team and region
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
# choose to sum or average game stats
        per_game = st.radio(
        "hidden",
        ('Per game stats', 'Total stats'),
        horizontal=True,label_visibility="hidden")

        if per_game=='Per game stats':
            per_game_bool = True
        else:
            per_game_bool = False

# filter by opponent and opponent region
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

# optionally filter by date 
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

# choose which statistical categories the user wants to see
# I don't want to present all of them at once to avoid crowding the table
    Stats_select = st.multiselect(
            'Statistical categories:',
            ["Base stats","Demos","Boost stats","Boost stats (Against)","Movement","Movement (Against)","Positioning","Positioning (Against)"],
            []
        )

# get all games  
    temp_df = team_meta_register

# get upper bound of games played
    max_GP = int(default_df['GP'].max())

#   filter by games played
    min_gp = st.slider(
        "Minimum Games Played:",
        0,max_GP, (0,max_GP)
        )

#   once query is submitted, filter temp_df
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
        # filter by region:
        if len(Region)!=0:
            temp_df = temp_df[temp_df["team_region"].isin(Region)]

        # filter by opposiong team:
        if len(teams_against)!=0:
            temp_df = temp_df[temp_df["opponent_name"].isin(teams_against)]
        # filter by opponent region:
        if len(Opponent_region)!=0:
            temp_df = temp_df[temp_df["opponent_region"].isin(Opponent_region)]

# filter by date:
        if date_check:
            temp_df = temp_df[(temp_df["game_date"]>=start_date) & (temp_df["game_date"]<=end_date)]


        stats_cats_dic = {
            "Base stats":team_base_stats,
            "Demos":team_demo_stats,
            "Boost stats":team_boost_stats_for,
            "Boost stats (Against)":team_boost_stats_against,
            "Movement":team_movement_stats_for,
            "Movement (Against)":team_movement_stats_against,
            "Positioning":team_positioning_stats_for,
            "Positioning (Against)":team_positioning_stats_against
        }

    
        
    


# merge with requested stat categories
# if no categories chosen, just return base stats
        if len(Stats_select)==0:
            temp_df = temp_df.merge(team_base_stats,on=["Team Name","Game Id"],how="left").drop(["Game Id",
                                                                                                "opponent_name",
                                                                                                "color",
                                                                                                "opponent_color",
                                                                                                "game_date",
                                                                                                "opponent_region",
                                                                                                "Split","Event Type","Event Sub-type"],axis=1)
        else:
# iterate through chosen categories and merge           
            for stats_cat in Stats_select:
                temp_df = temp_df.merge(stats_cats_dic[stats_cat],on=["Team Name","Game Id"],how="left")
            temp_df = temp_df.drop(["Game Id","opponent_name","color","opponent_color","game_date","opponent_region","Split","Event Type","Event Sub-type"],axis=1)

# aggregate stats
        display_df = aggregate_df(temp_df,list(temp_df.columns),per_game_bool)

# for per game stats, we round to one digit   
        if per_game_bool:
            display_df = display_df.apply(custom_round_1)
        else:
# for total stats, we take ints           
            display_df = display_df.apply(custom_round_0)
# filter by games played         
        display_df = display_df[(display_df['GP']>=min_gp[0]) & (display_df['GP']<=min_gp[1])]

# if the form hasn't been submitted, display the default table
    if not submitted:
        display_df = default_df
        display_df = display_df.apply(custom_round_1)


# use 'aggrid' to display the table
gb = GridOptionsBuilder.from_dataframe(display_df)

# define minimum column width
base_width = 80
# scale column width with length of column label
width_factor = 5

# set column configurations
for col in list(display_df.columns):

    col_len = len(col)

# pin 'Team Name' to the left of the table     
    if col == "Team Name":
        gb.configure_column(col, precision=1, width=190,pinned="left")
    elif col == "GP":
        gb.configure_column(col, precision=1, width=60)
    else:
        gb.configure_column(col, precision=1, width=(col_len*width_factor+base_width))


# display table, specify "NO_UPDATE" so it doesn't reload to the default every time the user sorts one of the columns
AgGrid(display_df, gridOptions=gb.build(),height=800,update_mode="NO_UPDATE")
