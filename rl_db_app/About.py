import streamlit as st
st.set_page_config(layout="wide",
                   page_title="RL-DB",
                   page_icon=":video_game:")


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


with st.sidebar:
    st.write("Select a page above.")

st.title("Welcome to RL-DB")
st.subheader("A project to collect and make accessible professional Rocket League stats.")

st.write("""
Select a page from the **sidebar** to find whatever stats interest you. At the moment, we have team stats and player stats for the 2022-2023 RLCS season.

This site is a personal project, and is still in development by me, James Kierans. For inquiries, contact me at contact@rl-db.com.

""")




st.text("")
st.text("")
st.header("Where do you get the data?")
st.write("""

All data has been collected from ballchasing.com and its API (consider supporting them on [Patreon](https://www.patreon.com/ballchasing) as I have).\
 Professional games gathered from ballchasing replay groups managed by [RLCS Referee](https://ballchasing.com/player/steam/76561199225615730)\
 and [RLStats](https://ballchasing.com/player/steam/76561199022336078), with team and player information cross-referenced with\
 [Liquipedia](https://liquipedia.net/rocketleague/Rocket_League_Championship_Series/2022-23).

""")


st.text("")
st.text("")
st.header("How did you make the site?")
st.write("""

The site is made with streamlit, a lightweight Python dashboarding app. Hosting done with Amazon Lightsail, on an Ubuntu\
 virtual machine. Backend database written in MySQL, hosted on Amazon RDS.



You can check out the backend for the site on my [github](https://github.com/kieransjames/rl-db.git).

""")






