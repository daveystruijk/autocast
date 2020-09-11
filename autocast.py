import os
import time
import random
import pychromecast
import googleapiclient.discovery
from pychromecast.controllers.youtube import YouTubeController
from dotenv import load_dotenv
load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
CHROMECAST_NAME = os.getenv('CHROMECAST_NAME')
PLAYLIST_ID = "PLDitloyBcHOm_Q06fztzSfLp19AJYX141"

youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = YOUTUBE_API_KEY)


def get_all_videos_in_playlist(playlist_id):
    request = youtube.playlistItems().list(
        part = "snippet",
        playlistId = playlist_id,
        maxResults = 50
    )
    response = request.execute()

    playlist_items = []
    while request is not None:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)
    return playlist_items

def get_random_video():
    videos = get_all_videos_in_playlist(PLAYLIST_ID)
    random_video = random.choice(videos)
    return random_video

def should_cast(status):
    return True

def cast_media(cast, url):
    yt = YouTubeController()
    cast.register_handler(yt)
    yt.play_video(url)

print(f"Waiting for chromecast '{CHROMECAST_NAME}'")
while True:
    try:
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[CHROMECAST_NAME])
        if len(chromecasts) > 0:
            print("Found chromecast!")
            cast = chromecasts[0]
            cast.wait()
            print(cast.status)
            if should_cast(cast.status):
                video = get_random_video()
                print(video['snippet']['resourceId'])
                cast_media(cast, video['snippet']['resourceId']['videoId'])
                break # return for now, we'll build a loop // deploy to raspi later
    except Exception as e:
        print(e)
    time.sleep(10)

