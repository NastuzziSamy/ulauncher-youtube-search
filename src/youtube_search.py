import urllib.parse
import requests
import json

from src.functions import clear_thumbnails, save_thumbnail


MAX_RESULTS = 10

SEARCH_BASE_URL = 'https://youtube.com/results?search_query='

BASE_URL = 'https://youtube.com'


class YoutubeSearch():
    def __init__(self, params):
        self.show_thumbnails = None
        self.query = ' '.join(params)

        clear_thumbnails()


    def has_query(self):
        return len(self.query) > 0


    def execute(self):
        response = requests.get(SEARCH_BASE_URL + urllib.parse.quote(self.query)).text
        results = []
        start = (
            response.index('ytInitialData') + len('ytInitialData') + 3
        )
        end = response.index('};', start) + 1

        data = json.loads(response[start:end])

        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']

        for content in contents:
            items = content.get('itemSectionRenderer', {}).get('contents', {})

            for item in items:
                if len(results) > MAX_RESULTS:
                    return results

                if 'videoRenderer' in item.keys():
                    video_data = item['videoRenderer']
                    video_id = video_data.get('videoId', None)
                    thumbnail = video_data.get('thumbnail', {}).get('thumbnails', [{}])[0].get('url', None)
                    thumbnail_path = None

                    if self.show_thumbnails and thumbnail:
                        thumbnail_path = save_thumbnail(thumbnail, video_id)

                    results.append({
                        'id': video_id,
                        'thumbnail': thumbnail_path,
                        'title': video_data.get('title', {}).get('runs', [{}])[0].get('text', '').replace('&', 'and'),
                        'channel': video_data.get('longBylineText', {}).get('runs', [{}])[0].get('text', None),
                        'date': video_data.get('publishedTimeText', {}).get('simpleText'),
                        'duration': video_data.get('lengthText', {}).get('simpleText', 0),
                        'views': video_data.get('viewCountText', {}).get('simpleText', 0),
                        'url': BASE_URL + video_data.get('navigationEndpoint', {}).get('commandMetadata', {}).get('webCommandMetadata', {}).get('url', None)
                    })

        return results