# Web Services Project

REST API built with Python and Flask that manages Students and Reports.

## Structure
- `phase1_lists`: storage with Python lists
- `phase2_dicts`: storage with dictionaries and auto-incremented IDs
- `phase2_auth` and `phase2_refresh`: JWT authentication, expiration and refresh token
- `homework_api`: final version, packaged with Docker
- `postman`: Postman collections to test the API

## Run with Docker
    cd homework_api
    docker build -t student-report-api .
    docker run -p 5000:5000 student-report-api

## Configuration (environment variables)
`PORT`, `SECRET_KEY`, `API_USERNAME`, `API_PASSWORD`, `ACCESS_TOKEN_MINUTES`, `REFRESH_TOKEN_MINUTES`

Example:
    docker run -p 8080:5000 -e ACCESS_TOKEN_MINUTES=1 -e API_PASSWORD=docker123 student-report-api

Default login: `admin` / `test123456`