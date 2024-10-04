#Annisa Risty

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px
sns.set(style='dark')

def bike_rentals_hourly(df):
    df['datetime'] = pd.to_datetime(df['dteday']) + pd.to_timedelta(df['hr'], unit='h')
    rent_hourly = df.resample(rule='H', on='datetime').agg({
        "instant": "nunique",  
        "cnt": "sum"  
    })
    rent_hourly = rent_hourly.reset_index()
    rent_hourly.rename(columns={
        "instant": "rental_count",
        "cnt": "total_rentals"
    }, inplace=True)
    
    return rent_hourly


def bike_rentals_by_season(df):
    rent_season = df.groupby(by="season").agg({
        "cnt": "sum",  
        "temp": ["max", "min", "mean", "std"]  
    })
    rent_season = rent_season.reset_index()
    
    return rent_season

def bike_rentals_by_weather(df):
    rent_weather = df.groupby(by="weathersit").agg({
        "cnt": "sum",  
        "hum": ["max", "min", "mean", "std"]  
    })
    rent_weather = rent_weather.reset_index()
    
    return rent_weather

def create_rfm_df(df):
    
    df['datetime'] = pd.to_datetime(df['dteday']) + pd.to_timedelta(df['hr'], unit='h')
    
    rfm_df = df.groupby(by="season", as_index=False).agg({
        "datetime": "max",  
        "instant": "nunique",  
        "cnt": "sum"  
    })
    
    rfm_df.columns = ["season", "max_rent_timestamp", "frequency", "monetary"]
    
    rfm_df["max_rent_timestamp"] = rfm_df["max_rent_timestamp"].dt.date
    recent_date = df["datetime"].dt.date.max()  
    rfm_df["recency"] = rfm_df["max_rent_timestamp"].apply(lambda x: (recent_date - x).days)
    
    rfm_df.drop("max_rent_timestamp", axis=1, inplace=True)
    
    return rfm_df

### MULAINYA DISINI

data_df = pd.read_csv("main_data.csv")

datetime_columns = ["dteday"]
data_df.sort_values(by="dteday", inplace=True)
data_df.reset_index(inplace=True)

for column in datetime_columns:
    data_df[column] = pd.to_datetime(data_df[column])

min_date = data_df["dteday"].min()
max_date = data_df["dteday"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = data_df[(data_df["dteday"] >= str(start_date)) & 
                (data_df["dteday"] <= str(end_date))]

rent_hourly = bike_rentals_hourly(main_df)
rent_season = bike_rentals_by_season(main_df)
rent_weather = bike_rentals_by_weather(main_df)
rfm_df = create_rfm_df(main_df) 

st.header('Ars Bike Rents :sparkles:')
st.caption('By: Annisa Risty :heart:')
st.subheader('Daily Orders')

total_rentals = main_df["cnt"].sum()  
st.metric("Total Bike Rentals", value=total_rentals)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    main_df["dteday"],  
    main_df["cnt"],     
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_xlabel("Date", fontsize=15)
ax.set_ylabel("Bike Rentals", fontsize=15)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=12, rotation=45)
st.pyplot(fig)

#pie chart for the seasons
season_rentals = main_df.groupby('season')['cnt'].sum().reset_index()
season_labels = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
season_rentals['season'] = season_rentals['season'].map(season_labels)

fig = px.pie(season_rentals, values='cnt', names='season', 
             title='Total Bike Rentals per Season',
             labels={'cnt': 'Total Rentals '},
             hole=0.3)  
st.plotly_chart(fig)

#for weathers
weathers_rentals = main_df.groupby('weathersit')['cnt'].sum().reset_index()

weathers_labels = {1: 'Clear', 2: 'Cloudy Mist', 3: 'Light Rain/Snow', 4: 'Heavy Rain'}
weathers_rentals['weathersit'] = weathers_rentals['weathersit'].map(weathers_labels)

fig = px.pie(weathers_rentals, values='cnt', names='weathersit', 
             title='Total Bike Rentals per Weather',
             labels={'cnt': 'Total Rentals '},
             hole=0.3) 
st.plotly_chart(fig)

average_duration = data_df['cnt'].mean()

st.subheader('Average Rental Duration')
st.metric("Average Rental Duration (in hours)", value=average_duration)

col1, col2 = st.columns(2)

with col1:
    fig_hist = px.histogram(data_df, x='cnt', nbins=30, title='Distribution of Rental Durations', 
                            labels={'cnt': 'Rental Duration (in hours)'}, 
                            marginal='box') 
    fig_hist.update_layout(xaxis_title='Rental Duration (in hours)', yaxis_title='Frequency')
    st.plotly_chart(fig_hist)

#boxplot
with col2:
    fig_box = px.box(data_df, x='cnt', title='Box Plot of Rental Durations', 
                     labels={'cnt': 'Rental Duration (in hours)'})
    fig_box.update_layout(xaxis_title='Rental Duration (in hours)')
    st.plotly_chart(fig_box)

data_df['dteday'] = pd.to_datetime(data_df['dteday'])
daily_rentals = data_df.groupby('dteday')['cnt'].sum().reset_index()
hourly_rentals = data_df.groupby('hr')['cnt'].sum().reset_index()

col1, col2 = st.columns(2)

#daily trends
with col1:
    fig_daily = px.line(daily_rentals, x='dteday', y='cnt', title='Daily Bike Rentals Trend',
                         labels={'dteday': 'Date', 'cnt': 'Total Rentals'}, markers=True)
    fig_daily.update_layout(xaxis_title='Date', yaxis_title='Total Rentals')
    st.plotly_chart(fig_daily)

#hourly trends
with col2:
    fig_hourly = px.line(hourly_rentals, x='hr', y='cnt', title='Hourly Bike Rentals Trend',
                          labels={'hr': 'Hour of the Day', 'cnt': 'Total Rentals'}, markers=True)
    fig_hourly.update_layout(xaxis_title='Hour of the Day', yaxis_title='Total Rentals')
    st.plotly_chart(fig_hourly)

##monthly trends
month_rentals = data_df.groupby(data_df['dteday'].dt.month)['cnt'].sum().reset_index()
month_rentals.rename(columns={'dteday': 'month'}, inplace=True)

fig_monthly = px.bar(month_rentals, x='month', y='cnt', title='Monthly Bike Rentals Trend',
                      labels={'month': 'Month', 'cnt': 'Total Rentals'},
                      color='month', color_continuous_scale=px.colors.sequential.Viridis)

fig_monthly.update_layout(xaxis_title='Month', yaxis_title='Total Rentals',
                           xaxis=dict(tickvals=list(range(1, 13)),  # Convert range to list
                                      ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
                           showlegend=False)  

st.plotly_chart(fig_monthly)

#casual vs registered
user_pie = pd.DataFrame({
    'Category': ['Casual', 'Registered'],
    'Count': [data_df['casual'].sum(), data_df['registered'].sum()]
})

fig = px.pie(user_pie, values='Count', names='Category',
             title='Casual vs Registered Users',
             color='Category',
             color_discrete_sequence=px.colors.qualitative.Set3,
             hole=0.3) 

st.plotly_chart(fig)
st.caption('Casual user: ')