# Mashify - Spotify Playlist Mashup Application

## Introduction
Let's say you are an avid Spotify user who has downloaded a large number of songs via playlists and albums. You want to make a new playlist called, for example, *dance*. However, you don't want to spend tons of time scouring through your playlists and albums to find all the songs that fit the new playlist. In this case, your best option is to use **Mashify**, a new app designed to help you create playlists by a set number of criteria.


## Overview
The app presents a UI capable of acting as a filter for a user's Spotify library. The final product allows the user to connect their Spotify account using the Spotify API, load their personal data into an SQLAlchemy database, and use the UI to filter their data by three criteria: artist, genre, and original playlist (within their own library). After doing so, the user may manually select and remove songs that were returned by the filter. When satisfied, the user may click "create playlist," give it a title, and within a few minutes, the new playlist should appear in your Spotify library.

To load your Spotify data, follow the instructions below!


## Getting Started

In the current state of the project, for the user to load their data, they must request access from the developer. For the time being, please:
1. email calam@wm.edu
2. with subject line 'Access Request For Mashify'

For Professor Smith:  
Use the Following Credentials  
user: 31n4tj7uvibaq7tj4agfn77bxuwy  
pass: SpotiTest123  

  
You can use these credential to login to our app as well as login to actual spotify on spotify.com to see the results  

Steps required to run the program:
1. Clone the repository
2. Use the command line to cd to the repository: `cd C:\path\to\repository`
3. Install libraries:
    1.  `pip install flask` or `pip3 install flask`
    2.  `pip install spotipy` or `pip3 install spotipy`
    3.  `pip install SQLAlchemy` or `pip3 install SQLAlchemy`
4. `flask --app main run --debug --port 3000`
5. Copy http url (localhost) and paste into web browser

Please view this [video](https://youtu.be/tnqCwi52IyY) for a step-by-step walkthrough on how to run the program.


When you've loaded into the web app through your browser:
1. Log in with your Spotify credentials
2. Click *Agree* when prompted by Timeify
3. Select the criteria you'd like to use as your filter
4. Manually select any songs you'd like to add/remove from the new playlist
5. Give your playlist a title, and create!


## Files Included
- [Mashify Final Report](https://drive.google.com/file/d/1ComNQA-iiyx_qyYGXwdElqG7Kiurs1Ik/view?usp=sharing). Contains detailed explanation of motivation, data descriptions, methods, output/functionality, future work, and contributions.
- `src/`: This directory contains the all of the code, including data scraping, database loading, and connection to UI. The code is documented with docstrings and comments throughout.
- `static/`: Contains CSS stylizing files for UI, commands the design and layout of the web app.
- `templates/`: Contains HTML files for content present in UI.
- `figures/`: Contains figures that may aid understanding of the project, such as ERD's, screenshots of UI, etc.
- `instance/`: Stores the database after the user has loaded in their data.


Authors: Cynthia Lam, Scooter Norton, Luke Schleck

Last Updated 17 December 2024



