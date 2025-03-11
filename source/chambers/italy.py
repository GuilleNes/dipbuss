import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_italy(url, country, events, country_chambers):

    if country == "Italy":

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        img_list = [
            img_tag.find("img").get("data-src")
            for img_tag in soup.find_all('div', class_='img-wrap')
        ]

        event_tags = soup.find_all('div', class_='post-content')

        for event_tag, img_url in zip(event_tags, img_list):
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
                    start_time = str(
                        int(start_time.split(" ")[1].split(":")[0]) + 12) + f":{start_time.split(':')[1]}"
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
                "img_url": img_url,
                "url": "https://iccj.or.jp",
                "chamber": country_chambers[country]
            })
    return events