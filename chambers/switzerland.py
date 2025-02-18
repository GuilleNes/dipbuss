import requests
from bs4 import BeautifulSoup
from utilities import month_map

def get_switzerland(url, country, events, country_chambers):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    for event_tag in soup.find_all("div", class_="em-item-info"):
        title = event_tag.find('h3').get_text(strip=True)

        href_tag = event_tag.find('h3', class_='em-item-title').find('a')
        href = href_tag['href'] if href_tag else None

        event_date_tag = event_tag.find(class_="event-date")
        if event_date_tag:
            event_date_tag = event_date_tag.get_text(strip=True, separator=" |")
            event_date = event_date_tag.split("|")[0] if "|" in event_date_tag else None
            time_range = event_date_tag.split("|")[1] if "|" in event_date_tag else None
            if time_range:
                start_time = time_range.split(" - ")[0]
                end_time = time_range.split(" - ")[1]
            else:
                start_time = end_time = None

            if event_date:
                try:
                    month, day, year = event_date.split()
                    day = day.strip(',')
                    month_numeric = month_map.get(month[:3], None)
                    if month_numeric:
                        event_date = f"{year}-{month_numeric}-{int(day):02d}"
                    else:
                        event_date = None
                except ValueError as e:
                    event_date = None
        else:
            event_date, start_time, end_time = None, None, None

        desc_tag = event_tag.find(class_="em-item-desc")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        events.append({
            "title": title,
            "href": href,
            "date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "url": "https://sccij.jp",
            "chamber": country_chambers[country]
        })
    return events