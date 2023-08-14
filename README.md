# music-collection-manager
Music Media Collection Manager


A small dashboard to help my dad with his music collection 

# Still in development stage

## With 
- Python
- Dash
- Plotly
- Mongodb
- Docker

## Create a Local Mongo Database in Docker 

```
docker run --name mongodb -d -e MONGO_INITDB_ROOT_USERNAME=<user> -e MONGO_INITDB_ROOT_PASSWORD=<pass>  -p 27017:27017 mongo

```

```
docker run -d --name MYAPP -e MONGODB_CONNSTRING=mongodb+srv://<user>:<pass>@localhost MYAPP:1.0

```
## If run with local DB

Create .env file with
```
CONNECTION_STRING=mongodb://<user>:<pass>@<host>
DATABASE=MEDIA
STAGE=DEV
DASH_DEBUG_MODE=True
DISCOGS_TOKEN=""
GOOGLE_AUTH_URL=https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent
GOOGLE_AUTH_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_REDIRECT_URI=""
GOOGLE_AUTH_USER_INFO_URL=https://www.googleapis.com/userinfo/v2/me
GOOGLE_AUTH_CLIENT_ID=""
GOOGLE_AUTH_CLIENT_SECRET=""

```