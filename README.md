# Premier League Stats App

A full-stack CRUD app for Premier League data:

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React (Vite)
- **Data:** scraped from Wikipedia, using the code from [premier-league-webscraper](https://github.com/moshaik1/premier-league-webscraper)

You can view the league table and top scorers, add/edit/delete rows, and click
**Refresh from Wikipedia** to replace everything with the latest data.

## How the pieces fit together

```
React (localhost:5173)  --/api/...-->  FastAPI (localhost:8000)  --SQL-->  PostgreSQL (localhost:5432)
                                              |
                                              +--> Wikipedia (only on Refresh)
```

Vite forwards every `/api` request to FastAPI (see `frontend/vite.config.js`), so the
browser only talks to one address.

## Project layout

```
backend/
  app/
    main.py          # creates the FastAPI app, the /api/scrape endpoint
    database.py      # connection to PostgreSQL
    models.py        # database tables (Team, Scorer)
    schemas.py       # shape of the JSON the API accepts/returns
    scraper.py       # Wikipedia scraping (BeautifulSoup + pandas)
    routers/
      teams.py       # CRUD endpoints for /api/teams
      scorers.py     # CRUD endpoints for /api/scorers
  requirements.txt
  .env.example       # copy to .env and add your database password
frontend/
  src/
    App.jsx          # page layout, tabs, Refresh button
    CrudTable.jsx    # reusable table with add/edit/delete
    api.js           # all fetch() calls to the backend
```

## Setup

### 1. PostgreSQL

1. Install PostgreSQL from https://www.postgresql.org/download/windows/ and remember the
   password you set for the `postgres` user.
2. Create the database (in a terminal; adjust `17` to your installed version):
   ```
   "C:\Program Files\PostgreSQL\17\bin\createdb.exe" -U postgres premier_league
   ```

### 2. Backend

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then edit .env and put in your password
uvicorn app.main:app --reload
```

The tables are created automatically on startup. Open http://localhost:8000/docs for
interactive API docs where you can try every endpoint.

### 3. Frontend

In a second terminal:

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and click **Refresh from Wikipedia** to load data.

## API

| Method | Path                 | What it does                         |
| ------ | -------------------- | ------------------------------------ |
| GET    | `/api/teams`         | List all teams in league order       |
| GET    | `/api/teams/{id}`    | Get one team                         |
| POST   | `/api/teams`         | Create a team                        |
| PUT    | `/api/teams/{id}`    | Update a team                        |
| DELETE | `/api/teams/{id}`    | Delete a team                        |
| ...    | `/api/scorers/...`   | Same five endpoints for top scorers  |
| POST   | `/api/scrape`        | Re-scrape Wikipedia, replace all data |
