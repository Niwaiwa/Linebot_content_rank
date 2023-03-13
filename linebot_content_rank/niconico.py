import requests
import time
from lxml import etree
import lxml.html

response_str = ""


class Niconico:

    main_url = "https://www.nicovideo.jp"
    rank_url = f"{main_url}/ranking/genre/all?video_ranking_menu"
    watch_url = "https://www.nicovideo.jp/watch/"

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    headers = {
        "user-agent": user_agent,
        "x-requested-with": "XMLHttpRequest",
    }

    name = "quotes"
    start_urls = [
        'https://www.nicovideo.jp/ranking/genre/all?video_ranking_menu',
    ]

    def __init__(self) -> None:
        pass

    def parse(self):
        pass

    def get_rank_data(self, mode="daily", page=1, format="json") -> dict:
        params = {
            # "mode": mode,
        }
        result = {}
        contents = []

        res = requests.get(self.rank_url, params, headers=self.headers)
        html_data = res.content

        html = lxml.html.fromstring(html_data)
        rank_class_element = html.find_class("NC-MediaObject NC-VideoMediaObject NC-VideoMediaObject_thumbnailWidth192 RankingMainVideo NC-MediaObject_withAction")
        
        for rank_element in rank_class_element:

            rank_num_elements = rank_element.find_class("RankingRowRank")
            for i in rank_num_elements:
                rank_num = int(i.text_content())

            title_class_elements = rank_element.find_class("NC-MediaObjectTitle NC-VideoMediaObject-title NC-MediaObjectTitle_fixed2Line")
            for title_element in title_class_elements:
                title_str = title_element.text_content()

            thumbnail_class_elements = rank_element.find_class("NC-Thumbnail-image")
            for thumbnail_element in thumbnail_class_elements:
                thumbnail_url = thumbnail_element.attrib.get("data-background-image")

            video_id = rank_element.attrib.get("data-video-id")
            video_url = f"{self.watch_url}{video_id}"

            contents.append({
                "rank": rank_num,
                "title": title_str,
                "thumbnail_url": thumbnail_url,
                "video_url": video_url,
            })

        result.update({"contents": contents})
        return result


if __name__ == "__main__":
    print("123")
    c = Niconico()
    res = c.get_rank_data("daily", "1")
    from pprint import pprint
    pprint(res)