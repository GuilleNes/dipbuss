import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def get_france(url, country, events, country_chambers):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    for article in soup.find_all("article", class_="thumbnail thumbnail-inline"):
        title_tag = article.find("h2", class_="title")
        title = title_tag.text.strip() if title_tag else None

        a_tag = article.find("a")
        href = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
        if href:
            href = urljoin(url, href)

        time_tag = article.find("time")
        date = time_tag['datetime'] if time_tag and 'datetime' in time_tag.attrs else None

        if date:
            try:
                date_object = datetime.strptime(date, "%Y-%m-%d")
                date = date_object.strftime("%Y-%m-%d")
            except ValueError:
                date = None

        caption_div = article.find("div", class_="caption")
        if caption_div:
            description_tag = None
            for p_tag in caption_div.find_all("p"):
                if "label-group" not in p_tag.get("class", []):
                    description_tag = p_tag
                    break

            description = description_tag.text.strip() if description_tag else None
        else:
            description = None

        if description == "Evènements":
            description = None

        events.append({
            "title": title,
            "href": href,
            "date": date,
            "description": description,
            "url": "https://www.ccifj.or.jp",
            "chamber": country_chambers[country]
        })
    return events