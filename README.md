# Songs App
Interactive dashboard of popular songs' features with live data fetched from Billboard Top 100 Songs, Spotify, and Genius

-------------

### Order of the files to be run:
1. Step1_billboard_100_weekly_scrape.py (Billboard 100 web scrape)
2. Step2_spotify_scrape_bb100.py (Spotify API data extraction)
3. Step3_genius_scrape_all.ipynb (Genius API *see instructions below*)
4. Step4_(ALL FILES) (for parsing and inserting JSON files into sql db)
5. Step5_sqldb_2.ipynb (Txt to SQL db)


---

Important: Notes on Genius.com API OAuth2 access
- Please install "requests_oauthlib" package by running `pip install requests_oauthlib` before running notebook
- When running the .ipynb notebook, go to the AUTHORIZATION URL in your browser (go to the URL from the notebook cell output), log in to website using provided credentials, click "Approve" button, COPY the response URL and paste it back into the notebook

- You may be asked to log in to the Genius website when authenticating, see login info below:

Genius.com Login
---
Username: musketeers1128@gmail.com
Password: 5JL6wGJ1oqGD

---
"The purpose of using sqlite3 is to understand better how SQL and dbs work, and have all data in centralized location for easy access"

