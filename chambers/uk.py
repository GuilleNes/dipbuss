from bs4 import BeautifulSoup
from selenium import webdriver
from utilities import month_map
from datetime import datetime

def get_uk(url, country, events, country_chambers):

    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")

    for event_tag, time_tag in zip(
            soup.find_all("a", class_="link-to-eb event-listing-title"),
            soup.find_all("div", class_="event-date")
    ):
        href = event_tag.get('href')
        title = event_tag.get_text(strip=True) if event_tag.get_text() else None

        dates = time_tag.get_text()
        date_parts = dates.split(" | ")

        event_date = date_parts[0].strip()
        parts = event_date.split()

        if len(parts) < 3:
            continue

        day = parts[0]
        month_str = parts[1]
        month = month_map.get(month_str, "01")
        year = parts[2]

        date_string = f"{year}-{month}-{day.zfill(2)}"
        try:
            date_object = datetime.strptime(date_string, "%Y-%m-%d")
            event_date = date_object.strftime("%Y-%m-%d")
        except ValueError:
            print(f"Error converting date: {event_date}")
            continue

        start_time, end_time = None, None
        if len(date_parts) > 1:
            time_parts = date_parts[1].split(" - ")
            if len(time_parts) == 2:
                start_time, end_time = time_parts[0].strip(), time_parts[1].strip()

                # Convert times to 24-hour format
                def convert_time(time_str):
                    try:
                        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
                    except ValueError:
                        return time_str  # Keep original if conversion fails

                start_time = convert_time(start_time)
                end_time = convert_time(end_time)

        events.append({
            "title": title,
            "date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "href": href,
            "url": "https://bccjapan.com",
            "chamber": country_chambers[country]
        })

    driver.quit()

    return events