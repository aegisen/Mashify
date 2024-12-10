# Mashify - Spotify Playlist Mashup Application

## Introduction
Let's say, you are an avid Spotify user, who has downloaded a large number of songs via playlists and albums. You want to make a new playlist, let's say, *dance*. However, you don't want to spend tons of time scouring through your playlists and albums to find all the songs that fit the new playlist. In this case, your best option is to use **Mashify**, a new app designed to help you create playlists by a set number of criteria.

## Overview
The app will present a UI capable of acting as a filter for a user's Spotify library. The final product will allow the user to connect their Spotify account using the Spotify API, load their personal data into a SQLAlchemy database, and use the UI to filter their data by several criteria: artist, genre, duration, playlist (within their own library), and release date. To load your Spotify data, follow the instructions below!

## Getting Started

In the current state of the project, we have yet to get past the point of letting the user load their data unless they use the developer's clientID and client secret. For the time being, please:
1. email calam@wm.edu
2. with subject line 'Access Request For Mashify'

Steps required to run the program:
1. Clone the repository
2. Use the command line to cd to the repository: `cd C:\path\to\repository`
3. Install libraries:
    1.  `!pip install flask` or `pip3 install flask`
    2.  `!pip install spotipy` or `pip3 install spotipy`
4. Set up virtual environment using flask: `python -m venv C:\path\to\new\virtual\environment flask`
5. cd back to repository
6. `!pip install -r requirements.txt` or `!pip3 install -r requirements.txt`
7. `flask --app app run --debug --port 3000`

8. If you encounter errors loading your data in to the database, try copying the localhost link and pasting directly into your web browser after completing the rest of the instructions

## App.py
Full documentation will be available soon

## Files Included
- Link to [Project Proposal & Progress](https://drive.google.com/file/d/1_TW8LrLPcaAd9Z4jfYDBFQ_Xuh82uEou/view?usp=sharing)



