# data-vis-for-humanities
Undocumented Immigration Data Visualization and Reddit Sentiment Analysis 

## Description
This project visualizes undocumented immigration data across US states from 2010 to 2019 using a choropleth map. It also performs sentiment analysis on Reddit posts and comments related to immigration topics. The application is built using Streamlit, Plotly, and Python.

## File Structure
project-folder/
├── data/
│   ├── gz_2010_us_040_00_500k.json  # Geographic data for US states
│   └── CMS-data-undoc-state_2010-2019.csv  # Immigration data by state
├── app.py  # Streamlit application code
├── requirements.txt  # List of Python dependencies
└── README.md  # This file

## Requirements
To run this, you need the Python Libraries which can be found in requirements.txt. Run the following command to install these files:
pip install -r requirements.txt

## Download NLTK Data
Run the following Python code to download the required NLTK data:
import nltk
nltk.download("vader_lexicon")

## Reddit API Credentials
Client_id and client_secret is available in app.py but if there is any trouble, its very easy to get a Reddit API. Create one at the Reddit Developer Portal: https://www.reddit.com/prefs/apps

## Run Streamlit App
Run the following command in your terminal:
streamlit run app.py

## Usage
Immigration Data Visualization:
    Select a year using the slider to view undocumented immigration data for that year.
    The choropleth map will update automatically.

Reddit Sentiment Analysis:
    Enter a search query (e.g., "Illegal Immigration") in the sidebar.
    Select subreddits to analyze (e.g., "Trump", "wall").
    Click "Fetch Data" to retrieve and analyze Reddit posts and comments.
    View sentiment distribution and word clouds for positive, neutral, and negative sentiments.



# Data Sources
Geographic Data:
    File: gz_2010_us_040_00_500k.json
    Source: US Census Bureau

Immigration Data:
    File: CMS-data-undoc-state_2010-2019.csv
    Source: Center for Migration Studies

