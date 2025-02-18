import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def get_deutschland(url, country, events, country_chambers):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    for event_tag in soup.find_all("article", class_="article is-top-theme"):

        title_tag = event_tag.find("a", class_="image-link")
        title = title_tag['title'] if title_tag else "No title available"

        time_tag = event_tag.find("time", class_="g-is-visuallyhidden")
        startime_tag = event_tag.find("div", class_="time typo:m")

        href_tag = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None

        if time_tag and 'datetime' in time_tag.attrs:
            date = time_tag['datetime']
            try:
                date_object = datetime.strptime(date, "%Y/%m/%d")  # Adjust this format as needed
                date = date_object.strftime("%Y-%m-%d")
            except ValueError:
                date = None

        if startime_tag:
            start_time = startime_tag.text.strip()

        if href_tag:
            href = urljoin(url, href_tag)
        else:
            href = None

        events.append({
            "title": title,
            "href": href,
            "date": date,
            "start_time": start_time,
            "url": "https://japan.ahk.de/en",
            "chamber": country_chambers[country]
        })
    return events