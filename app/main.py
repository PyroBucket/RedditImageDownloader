import json
import random
from databases import Database
from fastapi import FastAPI
import praw
from fastapi.responses import JSONResponse
from app.models import Image, TimestampedImage

# load config globals from json file
with open("app/config.json") as config_file:
    data_config = json.load(config_file)
    CLIENT_ID = data_config["client_id"]
    CLIENT_SECRET = data_config["client_secret"]
    PASSWORD = data_config["password"]
    USER_AGENT = data_config["user_agent"]
    USERNAME = data_config["username"]
    SUBREDDIT = data_config["subreddit"]

app = FastAPI()
# FastAPI docs of this app available at /docs
database = Database("sqlite:///app/images.db")


# make sure local database for image history exists
@app.on_event("startup")
async def database_connect():
    await database.connect()
    await database.execute("CREATE TABLE IF NOT EXISTS IMAGES ("
                           "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                           "url TEXT,"
                           "Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);")


# cleanup, close database connection
@app.on_event("shutdown")
async def database_disconnect():
    await database.disconnect()


@app.get("/")
async def root():
    return ["Documentation at /docs",
            "endpoints available:",
            "/random",
            "/history"]


# /random endpoint, response_model and responses defined for automatic documentation
@app.get("/random", response_model=Image, responses={406: {}})
async def fetch_random_image():
    # configure reddit client with data from config file
    # praw is a Reddit API wrapper for script applications
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        password=PASSWORD,
        user_agent=USER_AGENT,
        username=USERNAME,
    )
    sub = reddit.subreddit(SUBREDDIT)
    submissions = list(sub.top(time_filter="day", limit=100))
    random.shuffle(submissions)
    image_extensions = ["jpg", "png", "gif", "bmp"]
    for submission in submissions:
        image_url = submission.url
        extension = image_url.split('.')[-1]  # get everything after last '.' in url
        if extension in image_extensions:
            res = image_url
            break
    else:
        # 406 Not Acceptable response, server cannot produce a response matching criteria.
        # Will happen when given subreddit forbids image posts or there are no images in top 100 posts of the day
        return JSONResponse(status_code=406)

    # Insert found image to database No need to supply a timestamp because it's added by the database itself as
    # timestamp column defaults to current timestamp
    await database.execute(query="""
        INSERT INTO IMAGES
        (url)
        VALUES(:url)""", values={"url": res})
    return Image(link=res)


@app.get("/history", response_model=list[TimestampedImage])
async def get_history():
    image_data = await database.fetch_all("SELECT * FROM IMAGES")
    res = [TimestampedImage(url=row[1], timestamp=row[2]) for row in image_data]
    return res  # FastAPI automatically converts list to JSON, no need for manual conversion
