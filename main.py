import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from datetime import datetime
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
import json
from urllib.parse import urljoin
import time

load_dotenv()

## We create a map of months in order to iterate trough them in the future
month_map = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
    'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}

## Here we add the chambers url and country code in order to iterate on each
## We delete US and UK as we process them with Selenium later

def get_countries():
    country_chambers = {
        "Austria": "Austrian Embassy, Commercial Section (Advantage Austria)",
        "Belgium": "Belgian-Luxembourg Chamber of Commerce in Japan (BLCCJ)",
        "Canada": "Canadian Chamber of Commerce in Japan (CCCJ)",
        "Deutschland": "German Chamber of Commerce and Industry in Japan (AHK)",
        "Finland": "Finland Chamber of Commerce in Japan (FCCJ)",
        "France": "French Chamber of Commerce in Japan (CCIFJ)",
        "India": "Indian Chamber of Commerce in Japan (ICCJ)",
        "Ireland": "Ireland Chamber of Commerce in Japan (IJCC)",
        "Italy": "Italy Chamber of Commerce in Japan (ICCJ)",
        "Netherlands": "Netherlands Chamber of Commerce in Japan (NCCJ)",
        "Philippines": "Philippine Chamber of Commerce in Japan",
        "Spain": "Spanish Chamber of Commerce in Japan (SpCCJ)",
        "Sweden": "Sweden Chamber of Commerce in Japan (SCCJ)",
        "Switzerland": "Switzerland Chamber of Commerce in Japan (SCCIJ)",
        "UK": "British Chamber of Commerce in Japan (BCCJ)",
        "US": "American Chamber of Commerce in Japan (ACCJ)"
    }

    country_url = {
        "Belgium": "https://blccj.or.jp/events/list",
        "France": "https://www.ccifj.or.jp/en/events/upcoming-events.html",
        "Deutschland": "https://japan.ahk.de/en/events/coming-events",
        "Switzerland": "https://sccij.jp/events-future/",
        "Italy": "https://iccj.or.jp/upcoming-events/",
        "Canada": "https://www.cccj.or.jp/events",
        "Sweden": "https://www.sccj.org/events",
        "Spain": "https://spanishchamber.or.jp/upcoming-eventss/"
    }

    ## Variable para ejecutar una cámara determinada (desmarcar y completar if needed)

    # country_url = {"Italy": "https://iccj.or.jp/upcoming-events/"}

    events = []

    for key, value in country_url.items():
        url = value
        country = key

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        #### CANADA


        if country == "Canada":
            title_list = []
            href_list = []
            date_list = []
            startime_list = []
            endtime_list = []

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

            for title, event_date, start_time, end_time, href in zip(title_list, date_list, startime_list, endtime_list,
                                                                     href_list):
                events.append({
                    "title": title,
                    "date": event_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "href": href,
                    "url": "https://www.cccj.or.jp",
                    "chamber": country_chambers[country]
                })

        #### EJPAÑA
        if country == "Spain":

            for event_tag in soup.find_all("div", class_="tribe-events-calendar-list__event-wrapper tribe-common-g-col"):

                title_tag = event_tag.find("a")
                time_tag = event_tag.find("time")

                title = title_tag["title"] if title_tag else "No Title"
                href = title_tag["href"] if title_tag else "No Link"
                event_date = time_tag["datetime"] if time_tag and "datetime" in time_tag.attrs else "No Date"
                description = event_tag.find("p").get_text(strip=True)

                start_time = None
                if time_tag:
                    startime_tag = time_tag.find(class_="tribe-event-date-start")
                    if startime_tag:
                        startime_text = startime_tag.get_text(strip=True)
                        if "@ " in startime_text:
                            startime_raw = startime_text.split("@ ")[1]  # Extract time after "@ "
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
                    "url": "https://spanishchamber.or.jp",
                    "chamber": country_chambers[country]
                })

        #### SWEDEN

        if country == "Sweden":

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

        ##### SUIZA

        if country == "Switzerland":
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

        #### ITALY

        if country == "Italy":
            for event_tag in soup.find_all('div', class_='post-content'):
                title = event_tag.find('h2').get_text(strip=True)

                href_tag = event_tag.find('h2').find('a')
                href = href_tag['href'] if href_tag else None

                details = event_tag.find('p').get_text(strip=True)

                from_index = details.find("From:")
                to_index = details.find("to:")
                venue_index = details.find("Venue:")

                start_time = details[from_index + 5:to_index].strip() if from_index != -1 and to_index != -1 else None
                end_time = details[to_index + 3:venue_index].strip() if to_index != -1 and venue_index != -1 else None

                if start_time:
                    date_string = start_time.split(" ")[0]
                    try:
                        date_object = datetime.strptime(date_string, "%d/%m/%Y")
                        event_date = date_object.strftime("%Y-%m-%d")
                    except ValueError:
                        event_date = None
                else:
                    event_date = None

                if start_time:
                    if "PM" in start_time:
                        start_time = str(int(start_time.split(" ")[1].split(":")[0]) + 12) + f":{start_time.split(':')[1]}"
                        start_time = start_time.replace(" PM", "").strip()
                    elif "AM" in start_time:
                        start_time = start_time.replace(" AM", "").strip()
                        start_time = start_time.split(" ")[1]

                if end_time:
                    if "PM" in end_time:
                        end_time = end_time.replace(" PM", "").strip()
                        end_time = str(int(end_time.split(" ")[1].split(":")[0]) + 12) + f":{end_time.split(':')[1]}"
                    elif "AM" in end_time:
                        end_time = end_time.replace(" AM", "").strip()
                        end_time = end_time.split(" ")[1]

                if any(e["title"] == title and e["href"] == href for e in events):
                    continue

                events.append({
                    "title": title,
                    "href": href,
                    "date": event_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "url": "https://iccj.or.jp",
                    "chamber": country_chambers[country]
                })

        ##### GERMANY

        if country == "Deutschland":

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

        #### FRANCE

        if country == "France":

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

        ### BELGIUM

        if country == "Belgium":

            date_list = []

            for event_tag in soup.find_all("div",
                                           class_="tribe-events-calendar-list__event-datetime-wrapper tribe-common-b2"):
                time_tag = event_tag.find("time", class_="tribe-events-calendar-list__event-datetime")
                if time_tag and "datetime" in time_tag.attrs:
                    date_list.append(time_tag["datetime"])

            for index, event_tag in enumerate(
                    soup.find_all("a", class_="tribe-events-calendar-list__event-title-link tribe-common-anchor-thin")):
                title = event_tag.text.strip()
                href = event_tag['href']

                date = date_list[index] if index < len(date_list) else None

                time_tag = event_tag.find_next("time", class_="tribe-events-calendar-list__event-datetime")
                start_time, end_time = None, None

                if time_tag:
                    start_span = time_tag.find("span", class_="tribe-event-date-start")
                    if start_span and "@ " in start_span.text:
                        start_time = start_span.text.strip().split("@ ")[1]

                    end_span = time_tag.find("span", class_="tribe-event-time")
                    if end_span:
                        end_time = end_span.text.strip()

                if start_time:
                    start_time = start_time.lower().replace(" ", "")
                    if "pm" in start_time:
                        hour, minute = map(int, start_time.replace("pm", "").split(":"))
                        if hour != 12:  # 12 PM should remain 12
                            hour += 12
                        start_time = f"{hour}:{minute:02d}"
                    elif "am" in start_time:
                        hour, minute = map(int, start_time.replace("am", "").split(":"))
                        if hour == 12:  # 12 AM should become 00
                            hour = 0
                        start_time = f"{hour}:{minute:02d}"

                if end_time:
                    end_time = end_time.lower().replace(" ", "")
                    if "pm" in end_time:
                        hour, minute = map(int, end_time.replace("pm", "").split(":"))
                        if hour != 12:
                            hour += 12
                        end_time = f"{hour}:{minute:02d}"
                    elif "am" in end_time:
                        hour, minute = map(int, end_time.replace("am", "").split(":"))
                        if hour == 12:
                            hour = 0
                        end_time = f"{hour}:{minute:02d}"

                description_tag = event_tag.find_next("div",
                                                      class_="tribe-events-calendar-list__event-description tribe-common-b2 tribe-common-a11y-hidden")
                description = description_tag.text.strip() if description_tag else "No description available"

                events.append({
                    "title": title,
                    "href": href,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": description,
                    "url": "https://blccj.or.jp",
                    "chamber": country_chambers[country]
                })




    country_url = {"US": "https://www.accj.or.jp/accj-events",
                   "UK": "https://bccjapan.com/events/"}

    for key, value in country_url.items():
        url = value
        country = key


    #### UK

        if country == "UK":
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
                    "url":"https://bccjapan.com",
                    "chamber": country_chambers[country]
                })

            driver.quit()

    #### US

        if country == "US":
            driver = webdriver.Chrome()
            driver.get(url)
            html = driver.page_source
            time_regex = r"\d{1,2}:\d{2}"
            soup = BeautifulSoup(html, "html.parser")

            title_list = []
            date_list = []
            start_time_list = []
            end_time_list = []

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

            for title, event_date, start_time, end_time in zip(title_list, date_list, start_time_list, end_time_list):
                events.append({
                    "title": title,
                    "date": event_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "href": "https://www.accj.or.jp/accj-events",
                    "url": "https://www.accj.or.jp",
                    "chamber": country_chambers[country]
                })

            driver.quit()

    for event in events:
        try:
            if datetime.strptime(event["date"], "%Y-%m-%d") < datetime.now():
                events.remove(event)
        except Exception as e:
            print(f"Error fetching events: {e}")
            pass


    return events



## Now we execute the code in order to upload everything to the wordpress


class EventCrawlerPipeline:
    def __init__(self):
        self.wp_url = os.getenv('WP_URL')
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.42.0'
        }
        self.wp_user = os.getenv('WP_USER')
        self.wp_password = os.getenv('WP_PASSWORD')
        self.auth = HTTPBasicAuth(self.wp_user, self.wp_password)
        self.events = get_countries()

        query_params = {
            'per_page': 100
        }
        response = requests.get(self.wp_url, params=query_params, headers=self.headers, auth=self.auth)
        self.wordpress_events_status_code = response.status_code
        if response.status_code == 200:
            if response.text:
                wordpress_events = json.loads(response.text).get('events', [])
                self.wordpress_events = wordpress_events
            else:
                print("No content returned.")
        elif self.wordpress_events_status_code in [400, 403, 404, 500]:
            print(f"Error fetching events: {response.status_code} - {response.text}")

    def delete_old_events_wordpress(self):
        """Delete all events before today from WordPress API with pagination."""
        today = datetime.today().strftime('%Y-%m-%d')
        # today = "2026-01-01"    ##########################################################################################
        page = 1
        deleted_count = 0

        while True:
            response = requests.get(
                f"{self.wp_url}?start_date=2000-01-01&end_date={today}&per_page=100&page={page}",
                auth=self.auth, headers=self.headers
            )

            if response.status_code != 200:
                print(f"Error fetching events: {response.status_code} - {response.text}")
                break

            try:
                events = response.json().get('events', [])
            except Exception as e:
                print(f"Failed to parse response JSON: {e}")
                break

            if not events:
                break

            for event in events:
                event_id = event.get('id')
                title = event.get('title', 'Unknown Title')
                organizer = event.get("organizer", [{}])[0].get("organizer", "Unknown Organizer")

                delete_url = f"{self.wp_url}/{event_id}?force=true"
                delete_response = requests.delete(delete_url, auth=self.auth, headers=self.headers)

                if delete_response.status_code == 200:
                    deleted_count += 1
                    print(f"Deleted event {event_id} - {title} - {organizer}")
                else:
                    print(f"Failed to delete event {event_id}: {delete_response.text}")
            time.sleep(10)

            page += 1

        print(f"Total events deleted: {deleted_count}")

    def fetch_existing_events(self):
        """Fetch all events from WordPress and store them for quick lookup."""
        self.existing_events = []
        page = 1

        while True:
            query_params = {
                'per_page': 100,
                'page': page
            }
            response = requests.get(self.wp_url, params=query_params, headers=self.headers, auth=self.auth)

            if response.status_code != 200:
                print(f"Error fetching events: {response.status_code} - {response.text}")
                break

            events = response.json().get('events', [])
            if not events:
                break

            self.existing_events.extend(events)
            page += 1

    def format_datetime_iso(self, date_string, time_string=None):
        """Convert date and time into ISO format (YYYY-MM-DDTHH:MM:SS)."""
        try:
            if not date_string or date_string.lower() == "invalid date":
                print(f"Warning: Received invalid date '{date_string}', skipping...")
                return None  # Don't attempt to parse

            date = datetime.strptime(date_string.strip(), '%Y-%m-%d')

            if time_string:
                try:
                    time_obj = datetime.strptime(time_string.strip(), '%H:%M').time()
                except ValueError:
                    print(f"Invalid time format: {time_string}. Defaulting to 00:00.")
                    time_obj = datetime.strptime('00:00', '%H:%M').time()
            else:
                time_obj = datetime.strptime('00:00', '%H:%M').time()

            combined = datetime.combine(date, time_obj)
            return combined.strftime('%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            print(f"Error formatting date/time: {e}. Received date_string='{date_string}', time_string='{time_string}'")
            return None  # Prevent crash on invalid date

    def is_duplicate_event(self, title, start_date, chamber):
        """Check if an event with the given title, start date, and chamber already exists."""
        formatted_date = start_date.split("T")[0]

        for event in self.existing_events:
            event_start_date = event['start_date'].split(" ")[0]
            event_title = event['title'].strip().lower()
            event_chamber = event.get('organizer', [{}])[0].get('organizer', '')

            if event_title == title.lower() and event_start_date == formatted_date and event_chamber == chamber:
                return True  # Duplicate found

        return False  # No duplicate


    def process_item(self):
        """Process each event and send it to WordPress API efficiently."""
        events = self.events
        processed_events = []

        # First, delete old events
        self.delete_old_events_wordpress()

        # Fetch all existing events once and store them
        self.fetch_existing_events()

        for event in events:
            title = event.get('title', '').strip()
            raw_date = event.get('date', '')

            if not raw_date or raw_date.lower() == "invalid date":
                print(f"Skipping event '{title}' due to invalid date: {raw_date}")
                continue  # Skip this event

            start_time = event.get('start_time', '')
            end_time = event.get('end_time', '')

            start_date = self.format_datetime_iso(raw_date, start_time)
            end_date = self.format_datetime_iso(raw_date, end_time)

            description = event.get("description")
            if description is not None:
                try:
                    description = description.replace(u'\xa0', u' ')
                except:
                    pass
            else:
                description = " "

            # Check for duplicates in stored WordPress events
            if self.is_duplicate_event(title, start_date, event.get('chamber', '')):
                print(f"Duplicate event '{title}' detected. Skipping upload.")
                continue

            event_data = {
                'title': title,
                'description': description,
                'start_date': start_date,
                'end_date': end_date,
                'all_day': False,
                'timezone': 'Asia/Tokyo',
                'cost': event.get('cost', ''),
                'website': event.get('href', ''),
                'organizer': [{
                    'organizer': event.get('chamber', ''),
                    'website': event.get('url', ""),
                }],
                'show_map': True,
                'show_map_link': True
            }

            try:
                response = requests.post(self.wp_url, json=event_data, headers=self.headers, auth=self.auth)
                if response.status_code == 201:
                    event_id = response.json().get('id')
                    print(f"Event '{title}' created successfully: {event_id}")
                    processed_events.append(event_data)
                else:
                    print(f"Failed to create event: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error sending event '{title}' to API: {e}")

        return processed_events


# MAIN: Run locally
if __name__ == "__main__":
    pipeline = EventCrawlerPipeline()
    pipeline.process_item()