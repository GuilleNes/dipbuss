import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
import os
import json
import time


### We import the utilities

from utilities import country_url
from utilities import country_url_sel

### We import the functions
from functions import get_countries

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
        self.events = get_countries(country_url, country_url_sel)

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
