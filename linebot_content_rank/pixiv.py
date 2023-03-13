import requests
import time


class Pixiv:

    main_url = "https://www.pixiv.net"
    user_url = f"{main_url}/users"
    illust_url = f"{main_url}/artworks"
    rank_url = f"{main_url}/ranking.php"
    mode = "daily"
    page = "p"
    format = "json"


    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    def __init__(self) -> None:
        pass

    def get_rank_data(self, mode="daily", page=1, format="json") -> dict:
        params = {
            "mode": mode,
            "p": page,
            "format": format,
            # "date": "20210918",
        }
        result = {}

        res = requests.get(self.rank_url, params, headers=self.headers)
        data = res.json()
        result = {
            "date": data.get('date'),
            "prev_date": data.get('prev_date'),
        }
        contents = []
        image_list = []
        for info in data.get("contents", []):
            orig_url = info.get("url")
            url = self.get_proxy_image_url(orig_url)
            contents.append({
                "rank": info.get("rank"),
                "title": info.get("title"),
                "url": url,
                "user_id": info.get("user_id"),
                "user_name": info.get("user_name"),
                "illust_id": info.get("illust_id"),
                "width": info.get("width"),
                "height": info.get("height"),
                "illust_url": self.get_illust_url(info.get("illust_id")),
                "user_url": self.get_user_url(info.get("user_id")),
            })
            image_list.append(orig_url)
        result.update({"contents": contents})

        return result


    def get_illust_url(self, illust_id) -> str:
        return f"{self.illust_url}/{illust_id}"

    def get_user_url(self, user_id) -> str:
        return f"{self.user_url}/{user_id}"

    def get_proxy_image_url(self, orig_url) -> str:
        proxy_domain = "i.pixiv.cat"
        return orig_url.replace("i.pximg.net", proxy_domain)


if __name__ == "__main__":
    print("123")
    c = Pixiv()
    res = c.get_rank_data("daily", "1")
    from pprint import pprint
    pprint(res)
    # for r in res:
    #     print(len(r))