import urllib.parse
import requests
import json


MAX_RESULTS = 10

SEARCH_BASE_URL = 'https://youtube.com/results?search_query='

BASE_URL = 'https://youtube.com'


class YoutubeSearch():
    def __init__(self, params):
        self.query = ' '.join(params)


    def has_query(self):
        return len(self.query) > 0


    def execute(self):
        response = requests.get(SEARCH_BASE_URL + urllib.parse.quote(self.query)).text
        results = []
        start = (
            response.index("ytInitialData") + len("ytInitialData") + 3
        )
        end = response.index("};", start) + 1

        data = json.loads(response[start:end])

        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"] \
            ["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

        for video in videos[:MAX_RESULTS]:
            res = {}
            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})

                results.append({
                    'id': video_data.get("videoId", None),
                    'thumbnail': video_data.get("thumbnail", {}).get("thumbnails", [{}])[0].get("url", None),
                    'title': video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None),
                    'channel': video_data.get("longBylineText", {}).get("runs", [[{}]])[0].get("text", None),
                    'date': video_data.get("publishedTimeText", {}).get("simpleText"),
                    'duration': video_data.get("lengthText", {}).get("simpleText", 0),
                    'views': video_data.get("viewCountText", {}).get("simpleText", 0),
                    'url': BASE_URL + video_data.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", None)
                })
        
        return results