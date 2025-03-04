import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_deutschland(url, country, events, country_chambers):
    seen_titles = set()
    base_url = url

    for page in range(1, 10):  # Arbitrary upper limit, stops on duplicates
        url = base_url.format(page)
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Page {page} not found. Stopping.")
            break

        soup = BeautifulSoup(response.content, "html.parser")


        event_tags = soup.find_all("article", class_=["article is-top-theme", "article"])

        if not event_tags:
            print("No more events found. Stopping.")
            break

        img_list = [img_tag.find("img").get("src") if img_tag.find("img") else "No Image"
                    for img_tag in soup.find_all("a", class_="image-link")]
        img_list = [urljoin(url, img) for img in img_list]

        for event_tag, img_url in zip(event_tags, img_list):
            title_tag = event_tag.find("a", class_="image-link")
            title = title_tag['title'] if title_tag else "No title available"
            href = urljoin(url, title_tag['href']) if title_tag and 'href' in title_tag.attrs else None

            if title in seen_titles:
                print(f"Duplicate event found: {title}. Stopping.")
                break

            seen_titles.add(title)  # Add title to seen set

            time_tag = event_tag.find("time", class_="g-is-visuallyhidden")
            date = time_tag['datetime'] if time_tag and 'datetime' in time_tag.attrs else None

            startime_tag = event_tag.find("div", class_="time typo:m")
            start_time = startime_tag.text.strip() if startime_tag else None

            events.append({
                "title": title,
                "href": href,
                "date": date,
                "start_time": start_time,
                "img_url": img_url,
                "url": "https://japan.ahk.de/en",
                "chamber": country_chambers[country]
            })


        else:
            print(f"Scraped Page {page} - {len(event_tags)} events found")
            continue
        break
    return events