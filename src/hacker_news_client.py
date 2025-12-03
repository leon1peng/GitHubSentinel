# src/hacker_news_client.py

import requests
from requests import Response
from bs4 import BeautifulSoup


class HackerNewsClient:
    domain_name = "https://news.ycombinator.com/"
    page_size = 30

    def __init__(self) -> None:
        pass

    def http_requests(self, page_index: int = 1):
        url = f"{self.domain_name}?p={page_index}"
        response = requests.get(url)
        return response

    def parser_http_data(self, response: Response):

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr", class_="athing")

        stories = []
        for row in rows:
            titleline = row.find("span", class_="titleline")
            if not titleline:
                continue
            a_tag = titleline.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            href = a_tag["href"]
            stories.append({"title": title, "link": href})
        return stories
    
    @staticmethod
    def convery_format(stories):
        result = ""
        for idx, story in enumerate(stories, start=1):
            result += f"{idx}. {story['title']}: {story['link']}\n"
        return result

    def fetch_hackernews_top_stories(self, top: int = 30):
        page_count = -(-top // self.page_size)
        all_top_stories = []
        for num in range(page_count):
            page_index = num + 1
            response = self.http_requests(page_index)
            
            top_stories = self.parser_http_data(response)
            all_top_stories.extend(top_stories)
        result = self.convery_format(all_top_stories)

        return result

if __name__ == "__main__":
    client = HackerNewsClient()
    stories = client.fetch_hackernews_top_stories()
    print(stories)

