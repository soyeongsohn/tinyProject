import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px
from os import path
from pathlib2 import Path

dirpath = Path(__file__).parent
DATA_URL = path.join(dirpath, "Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
"to analyze motor vehicle collisions in NYC🗽💥🚗")


@st.cache(persist=True) # decorator를 통해 cache 지속되게
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)

    return data

data = load_data(100000)

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injutred in vehicle collisions", 0, int(max(data.injured_persons)))
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of day?")
# hour = st.selectbox("Hour to look at", range(0, 24), 1)
# hour = st.sidebar.slider("Hour to look at", 0, 23)
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown(f"Vehicle Collisions between {hour}:00 and {(hour+1) % 24}:00")
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True, # 위로 기둥처럼 솟아오르게 함
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000]
        )
    ]
))

st.subheader(f"Breakdown by minute between {hour}:00 and {(hour + 1) % 24}:00")
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])
if select == 'Pedestrians':
    st.write(data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
    st.write(data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False): # check박스 클릭해제되어있을 때만 실행
    st.subheader('Raw Data')
    st.write(data)
