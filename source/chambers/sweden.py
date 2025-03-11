import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def get_sweden(url, country, events, country_chambers):

    if country == "Sweden":

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        for event_tag in soup.find_all("div", class_="col-sm-12 event-item-item"):

            title = event_tag.find("a").get_text(strip=True) if event_tag.find("a") else "No Title"
            href_tag = event_tag.find("a")["href"] if event_tag.find("a") else None

            time_tag = event_tag.find(class_="event-item-starttime").get_text(strip=True) if event_tag.find(
                class_="event-item-starttime") else None

            if time_tag:
                try:
                    date_part = ' '.join(time_tag.split()[0:3])
                    date_object = datetime.strptime(date_part, '%d %B %Y')
                    event_date = date_object.strftime('%Y-%m-%d')

                except Exception as e:
                    event_date = "No Date"
                try:
                    time_parts = time_tag.split(" ")
                    start_time = time_parts[3] if len(time_parts) > 3 else "Unknown"
                    end_time = time_parts[5] if len(time_parts) > 5 else "Unknown"
                except Exception as e:
                    start_time = "Unknown"
                    end_time = "Unknown"
            else:
                event_date = "No Date"
                start_time = "No Start Time"
                end_time = "No End Time"

            href = urljoin(url, href_tag) if href_tag else "No Link"

            events.append({
                "title": title,
                "href": href,
                "date": event_date,
                "start_time": start_time,
                "end_time": end_time,
                "url": "https://www.sccj.org",
                "chamber": country_chambers[country]
            })
    return events