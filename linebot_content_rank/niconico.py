import requests
import time
from lxml import etree
import lxml.html

response_str = ""


class Niconico:

    main_url = "https://www.nicovideo.jp"
    rank_url = f"{main_url}/ranking/genre/all"
    watch_url = "https://www.nicovideo.jp/watch/"

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    headers = {
        "user-agent": user_agent,
        "x-requested-with": "XMLHttpRequest",
    }

    name = "quotes"
    # start_urls = [
    #     'https://www.nicovideo.jp/ranking/genre/all?term=24h&page=1',
    # ]
    mode_map = {
        "daily": "24h",
        "weekly": "week",
        "monthly": "month",
    }

    def __init__(self) -> None:
        pass

    def parse(self):
        pass

    def param_page_calc(self, page):
        return (page // 2) + (page % 2)

    def get_rank_data(self, mode="daily", page=1, format="json") -> dict:
        page_param = self.param_page_calc(page)
        params = {
            "term": self.mode_map.get(mode, self.mode_map["daily"]),
            "page": f"{page_param}",
        }
        result = {}
        contents = []

        res = requests.get(self.rank_url, params, headers=self.headers)
        html_data = res.content

        html = lxml.html.fromstring(html_data)
        rank_class_element = html.find_class("NC-VideoMediaObjectWrapper")
        half_element = len(rank_class_element)//2
        if page % 2 == 1:
            rank_class_element = rank_class_element[:half_element]
        else:
            rank_class_element = rank_class_element[half_element:]

        for rank_element in rank_class_element:

            rank_num = "N/A"
            rank_num_elements = rank_element.find_class("RankingRowRank")
            for i in rank_num_elements:
                rank_num = int(i.text_content())

            title_str = "N/A"
            title_class_elements = rank_element.find_class("NC-MediaObjectTitle NC-VideoMediaObject-title NC-MediaObjectTitle_fixed2Line")
            for title_element in title_class_elements:
                title_str = title_element.text_content()

            thumbnail_url = None  # None will not to set image
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
    res = c.get_rank_data("daily", 1)
    from pprint import pprint
    pprint(res)
    