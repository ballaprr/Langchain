from dotenv import load_dotenv
from langchain import OpenAI
import streamlit as st 
from langchain.agents import create_csv_agent, initialize_agent, Tool
from llama_index import SimpleDirectoryReader, GPTListIndex, GPTVectorStoreIndex, LLMPredictor, PromptHelper, download_loader
from pathlib import Path
import openai
import pandas as pd
import requests
import re
import os

openai.api_key = ""

os.environ["OPENAI_API_KEY"] = ""


load_dotenv()

st.set_page_config(page_title="Baseball CSV")
st .header("Prompt: ")

year = st.text_input("Year: ")
if not year.isdigit():
    st.warning("Please enter a valid year.")
    st.stop()

url = ['player pitching', 'player hitting', 'team pitching', 'team hitting']

url_st = st.selectbox('Select data for analysis', url)
if url_st not in url:
    st.warning("Please select a valid analysis option.")
    st.stop()

if url_st == 'player pitching':
    player_pitching_url = "https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=" + year + "&sportId=1&stats=season&group=pitching&gameType=R&limit=25&offset=0&sortStat=earnedRunAverage&order=asc"
    r_player_pitching = requests.get(url=player_pitching_url).json()
    rows = []
    for i in range (0, 25):
        rows.append(list(r_player_pitching['stats'][i].values()))
    df_player_pitch = pd.DataFrame(rows, columns=list(r_player_pitching['stats'][0].keys()))

    df_player_pitch = df_player_pitch[df_player_pitch.keys()]

    df_player_pitch.to_csv(year + "_data_player_pitch.csv", index=False)
elif url_st == 'player hitting':
    player_hitting_url = "https://bdfed.stitch.mlbinfra.com/bdfed/stats/player?stitch_env=prod&season=" + year + "&sportId=1&stats=season&group=hitting&gameType=R&limit=25&offset=0&sortStat=onBasePlusSlugging&order=desc"
    r_player_hitting = requests.get(url=player_hitting_url).json()
    rows = []
    for i in range (0, 25):
        rows.append(list(r_player_hitting['stats'][i].values()))
    df_player_pitch = pd.DataFrame(rows, columns=list(r_player_hitting['stats'][0].keys()))

    df_player_pitch = df_player_pitch[df_player_pitch.keys()]

    df_player_pitch.to_csv(year + "_data_player_hitt.csv", index=False)
elif url_st == 'team pitching':
    team_hitting_url = "https://bdfed.stitch.mlbinfra.com/bdfed/stats/team?stitch_env=prod&sportId=1&gameType=R&group=hitting&order=desc&sortStat=onBasePlusSlugging&stats=season&season=" + year + "&limit=30&offset=0"
    r_team_hitting = requests.get(url=team_hitting_url).json()
    rows = []
    for i in range (0, 25):
        rows.append(list(r_team_hitting['stats'][i].values()))
    df_player_pitch = pd.DataFrame(rows, columns=list(r_team_hitting['stats'][0].keys()))

    df_player_pitch = df_player_pitch[df_player_pitch.keys()]

    df_player_pitch.to_csv(year + "_data_team_hitt.csv", index=False)
elif url_st == 'team hitting':
    team_pitching_url = "https://bdfed.stitch.mlbinfra.com/bdfed/stats/team?stitch_env=prod&sportId=1&gameType=R&group=pitching&order=asc&sortStat=earnedRunAverage&stats=season&season=" + year + "&limit=30&offset=0"
    r_team_pitching = requests.get(url=team_pitching_url).json()
    rows = []
    for i in range (0, 25):
        rows.append(list(r_team_pitching['stats'][i].values()))
    df_player_pitch = pd.DataFrame(rows, columns=list(r_team_pitching['stats'][0].keys()))

    df_player_pitch = df_player_pitch[df_player_pitch.keys()]

    df_player_pitch.to_csv(year + "_data_team_pitch.csv", index=False)


user_csv=st.file_uploader("Upload your CSV",type=["csv"])

def save_txt_content(content, filename):
    # Save the TXT content to a file
    with open(filename, "w") as txt_file:
        txt_file.write(content)


if user_csv is not None:

    SimpleCSVReader = download_loader("SimpleCSVReader")
    loader = SimpleCSVReader(encoding="utf-8")
    print(user_csv.name)
    docs = loader.load_data(file=Path(user_csv.name))

    vectorIndex = GPTVectorStoreIndex.from_documents(docs)
    query_engine = vectorIndex.as_query_engine()   
    response = query_engine.query("Summarize the data") 
    st.write(response.response)

    user_input=st.text_input("Ask a question about your CSV: ")

    #path = "data/data.csv"
    llm = OpenAI(temperature = 0)
    agent_csv = create_csv_agent(llm, user_csv.name, verbose=True)
    res = agent_csv.run(user_input)

    st.write(res)

    txt_content = f"Year:\n{year}\n"
    txt_content += f"Data\n{url_st}"
    txt_content += f"Summary\n{response.response}"
    txt_content += f"Question about your CSV\n{user_input}\n{res}\n"

    if st.button("Download Response as txt"):
        save_txt_content(txt_content, "responses.txt")
        st.success("TXT file saved!")





    # To DO
    # Figure out entering year
    # 

