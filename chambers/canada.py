import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_canada(url, country, events, country_chambers):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    title_list = []
    href_list = []
    date_list = []
    startime_list = []
    endtime_list = []
    img_list = []

    for event_tag in soup.find_all('h3', class_='node-title')[1:]:
        title = event_tag.get_text(strip=True)
        href_tag = event_tag.find("a")["href"]
        href = urljoin(url, href_tag) if href_tag else "No Link"

        title_list.append(title)
        href_list.append(href)

    for date_tag in soup.find_all(class_="node-teaser-content image"):
        event_date = date_tag.find(class_="date-display-single")["content"].split("T")[0]
        date_list.append(event_date)

    for times_tag in soup.find_all(class_="event-time"):
        start_time = times_tag.get_text(strip=True).split(" ~ ")[0]
        startime_list.append(start_time)
        end_time = times_tag.get_text(strip=True).split(" ~ ")[1]
        endtime_list.append(end_time)

    for img_tag in soup.find_all('img', class_="lozad animated"):
        img = img_tag.get("data-src")
        img_list.append(img)

    for title, event_date, start_time, end_time, img_url, href in zip(title_list, date_list, startime_list,
                                                                      endtime_list, img_list,
                                                                      href_list):
        events.append({
            "title": title,
            "date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "href": href,
            "img_url": img_url,
            "url": "https://www.cccj.or.jp",
            "chamber": country_chambers[country]
        })
    return events