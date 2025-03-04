from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def get_france(url, country, events, country_chambers):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without opening a browser window
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    load_more_xpath = "//a[contains(@class, 'btn-load') and contains(@class, 'icon-plus')]"
    prev_count = len(driver.find_elements(By.CSS_SELECTOR, "article.thumbnail.thumbnail-inline"))

    while True:
        try:
            load_more_button = wait.until(
                EC.presence_of_element_located((By.XPATH, load_more_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)

            clickable_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, load_more_xpath))
            )
            driver.execute_script("arguments[0].click();", clickable_button)

            wait.until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "article.thumbnail.thumbnail-inline")) > prev_count
            )
            prev_count = len(driver.find_elements(By.CSS_SELECTOR, "article.thumbnail.thumbnail-inline"))
            print(f"Loaded more events for France. Total events so far: {prev_count}")
            time.sleep(2)

        except TimeoutException:
            print("No more events found or button is not clickable")
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    img_list = [
        urljoin(url, img_tag.find("img")["src"]) if img_tag.find("img") else "No Image"
        for img_tag in soup.find_all("figure", class_="thumbnail-figure")
    ]
    event_tags = soup.find_all("article", class_="thumbnail thumbnail-inline")

    for article, img_url in zip(event_tags, img_list):
        title_tag = article.find("h2", class_="title")
        title = title_tag.text.strip() if title_tag else "No Title"

        a_tag = article.find("a")
        href = urljoin(url, a_tag["href"]) if a_tag and "href" in a_tag.attrs else "No Link"

        time_tag = article.find("time")
        date = time_tag["datetime"] if time_tag and "datetime" in time_tag.attrs else None
        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                date = "Invalid Date"

        caption_div = article.find("div", class_="caption")
        description = None
        if caption_div:
            description_tag = next(
                (p_tag for p_tag in caption_div.find_all("p") if "label-group" not in p_tag.get("class", [])), None
            )
            description = description_tag.text.strip() if description_tag else None
        if description == "Evènements":
            description = None

        events.append({
            "title": title,
            "href": href,
            "date": date,
            "description": description,
            "img_url": img_url,
            "url": "https://www.ccifj.or.jp",
            "chamber": country_chambers[country]
        })

    return events