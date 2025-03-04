from bs4 import BeautifulSoup
from selenium import webdriver
from utilities import month_map
from datetime import datetime

def get_uk(url, country, events, country_chambers):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    img_list = [img_tag.find("img").get("src") if img_tag.find("img") else None
                for img_tag in soup.find_all("a", class_="link-to-eb event-listing-thumbnails")]

    desc_list = [desc_tag.find("p").get_text(strip=True) if desc_tag.find("p") else None
                for desc_tag in soup.find_all("div", class_="event-description")]

    for event_tag, time_tag, img_url, description in zip(
            soup.find_all("a", class_="link-to-eb event-listing-title"),
            soup.find_all("div", class_="event-date"),
            img_list, desc_list
    ):
        href = event_tag.get('href')
        title = event_tag.get_text(strip=True) if event_tag.get_text() else "None"

        dates = time_tag.get_text()
        date_parts = dates.split(" | ")

        if len(date_parts) == 0:
            continue

        event_date = date_parts[0].strip()
        parts = event_date.split()

        if len(parts) < 3:
            continue

        day = parts[0].zfill(2)
        month_str = parts[1]
        year = parts[2]

        month = month_map.get(month_str, "01")

        date_string = f"{year}-{month}-{day.zfill(2)}"
        try:
            event_date = datetime.strptime(date_string, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Error converting date: {event_date}")
            continue

        start_time, end_time = None, None
        if len(date_parts) > 1:
            time_parts = date_parts[1].split(" - ")
            if len(time_parts) == 2:
                start_time, end_time = time_parts[0].strip(), time_parts[1].strip()

                def convert_time(time_str):
                    try:
                        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
                    except ValueError:
                        return "None"

                start_time = convert_time(start_time)
                end_time = convert_time(end_time)

        events.append({
            "title": title,
            "date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "href": href,
            "img_url": img_url,
            "description": description,
            "url": "https://bccjapan.com",
            "chamber": country_chambers[country]
        })

    driver.quit()

    return events