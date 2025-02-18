import requests
from bs4 import BeautifulSoup

def get_belgium(url, country, events, country_chambers):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

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
    return events