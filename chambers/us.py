from bs4 import BeautifulSoup
from selenium import webdriver
import re
import json

def get_us(url, country, events, country_chambers):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(20)
    html = driver.page_source

    time_regex = r"\d{1,2}:\d{2}"
    soup = BeautifulSoup(html, "html.parser")

    title_list = []
    date_list = []
    start_time_list = []
    end_time_list = []
    img_list = []

    for img_tag in soup.find_all("div", class_="jsx-1143752508 eapp-events-calendar-masonry-item-imageContainer"):
        img_url = img_tag.find("img").get("src")
        img_list.append(img_url)

    for event_tag in soup.find_all("div",
                                   class_="jsx-401363670 eapp-events-calendar-name-component eapp-events-calendar-masonry-item-name"):
        title = event_tag.text.strip()
        title_list.append(title)

    time_tags = soup.find_all("script", type="application/ld+json")
    for tag in time_tags:
        if "endDate" in json.loads(tag.text.strip()):
            try:
                event_date = json.loads(tag.text.strip())["endDate"]
                date_list.append(event_date)
            except:
                pass

    startime_tags = soup.find_all("div", class_="jsx-1364132950 eapp-events-calendar-time-text")
    for tag in startime_tags:
        times = tag.text.strip()
        try:
            # Extract start time
            start_time = times.split(" - ")[0]
            if "PM" in start_time:
                start_time = str(int(start_time.split(":")[0]) + 12) + f":{start_time.split(':')[1]}"
                start_time = start_time.replace("PM", "").strip()
                start_time = re.findall(time_regex, start_time)[0]
                start_time_list.append(start_time)

            elif "AM" in start_time:
                start_time = start_time.replace("AM", "").strip()
                start_time = re.findall(time_regex, start_time)[0]
                start_time_list.append(start_time)
            else:
                start_time = re.findall(time_regex, start_time)[0]
                start_time_list.append(start_time)

        except:
            start_time = "None"
            start_time_list.append(start_time)

        try:
            end_time = times.split(" - ")[1]
            if "PM" in end_time:
                end_time = str(int(end_time.split(":")[0]) + 12) + f":{end_time.split(':')[1]}"
                end_time = end_time.replace("PM", "").strip()
                end_time = re.findall(time_regex, end_time)[0]
                end_time_list.append(end_time)

            elif "AM" in end_time:
                end_time = end_time.replace("AM", "").strip()
                end_time = re.findall(time_regex, end_time)[0]
                end_time_list.append(end_time)

            else:
                end_time = re.findall(time_regex, end_time)[0]
                end_time_list.append(end_time)

        except:
            end_time = "None"
            end_time_list.append(end_time)

    for title, event_date, start_time, end_time, img_url in zip(title_list, date_list, start_time_list, end_time_list,
                                                                img_list):
        events.append({
            "title": title,
            "date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "href": "https://www.accj.or.jp/accj-events",
            "img_url": img_url,
            "url": "https://www.accj.or.jp",
            "chamber": country_chambers[country]
        })

    driver.quit()

    return events