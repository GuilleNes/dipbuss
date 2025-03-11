import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_canada(url, country, events, country_chambers):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")


    # Initialize lists for extracted data.
    title_list = []
    href_list = []
    date_list = []
    startime_list = []
    endtime_list = []
    img_list = []
    desc_list = []


    for event_tag in soup.find_all('div', class_='node-description'):
        desc = event_tag.find("p")
        desc_list.append(desc.get_text(strip=True) if desc else None)

    for event_tag in soup.find_all('h3', class_='node-title')[1:]:
        title = event_tag.get_text(strip=True)
        href_tag = event_tag.find("a")
        href = urljoin(url, href_tag["href"]) if href_tag and href_tag.get("href") else None

        title_list.append(title)
        href_list.append(href)

    for date_tag in soup.find_all(class_="node-teaser-content image"):
        date_element = date_tag.find(class_="date-display-single")
        event_date = date_element["content"].split("T")[0] if date_element and date_element.get(
            "content") else ""
        date_list.append(event_date)

    for times_tag in soup.find_all(class_="event-time"):
        time_text = times_tag.get_text(strip=True)
        if "~" in time_text:
            start_time, end_time = time_text.split(" ~ ", 1)
        else:
            start_time, end_time = None, None

        startime_list.append(start_time)
        endtime_list.append(end_time)

    for img_tag in soup.find_all('img', class_="lozad animated"):
        img = img_tag.get("data-src", None)
        img_list.append(img)

    for title, event_date, start_time, end_time, img_url, description, href in zip(title_list, date_list, startime_list,
                                                                      endtime_list, img_list, desc_list, href_list):
        events.append({
            "title": title,
            "date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "href": href,
            "img_url": img_url,
            "description": description,
            "url": "https://www.cccj.or.jp",
            "chamber": country_chambers[country]
        })
    return events