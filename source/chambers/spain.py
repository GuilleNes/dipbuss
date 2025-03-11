import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_spain(url, country, events, country_chambers):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    img_list = [
        img_tag.find("img").get("src")
        for img_tag in soup.find_all("div",
                                     class_="tribe-events-calendar-list__event-featured-image-wrapper tribe-common-g-col")
    ]

    event_tags = soup.find_all("div", class_="tribe-events-calendar-list__event-wrapper tribe-common-g-col")

    for event_tag, img_url in zip(event_tags, img_list):
        title_tag = event_tag.find("a")
        time_tag = event_tag.find("time")

        title = title_tag["title"] if title_tag else "No Title"
        href = title_tag["href"] if title_tag else "No Link"
        event_date = time_tag["datetime"] if time_tag and "datetime" in time_tag.attrs else "No Date"
        description = event_tag.find("p").get_text(strip=True) if event_tag.find("p") else "No Description"

        start_time = None
        if time_tag:
            startime_tag = time_tag.find(class_="tribe-event-date-start")
            if startime_tag:
                startime_text = startime_tag.get_text(strip=True)
                if "@ " in startime_text:
                    startime_raw = startime_text.split("@ ")[1]
                    try:
                        start_time = datetime.strptime(startime_raw, "%I:%M %p").strftime("%H:%M")
                    except ValueError:
                        start_time = "Invalid Start Time"

        end_time = None
        if time_tag:
            endtime_tag = time_tag.find(class_="tribe-event-time")
            if endtime_tag:
                endtime_text = endtime_tag.get_text(strip=True)
                try:
                    end_time = datetime.strptime(endtime_text, "%I:%M %p").strftime("%H:%M")
                except ValueError:
                    end_time = "Invalid End Time"

        events.append({
            "title": title,
            "href": href,
            "date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "img_url": img_url,
            "url": "https://spanishchamber.or.jp",
            "chamber": country_chambers[country]
        })

    return events