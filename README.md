📌 Web Scraper & WordPress API Connector
Automated event scraping and posting to a WordPress site

📖 Overview
This project automates the extraction of event data from various international chambers of commerce and uploads it to a WordPress site via the WordPress API.

🌍 Supported Countries & Sources
The scraper extracts event details from the following chambers of commerce:

Canada: https://www.cccj.or.jp
Spain: https://spanishchamber.or.jp
Sweden: https://www.sccj.org
Switzerland: https://sccij.jp
Italy: https://iccj.or.jp
Each country has its own HTML structure, requiring different parsing logic.

⚙️ Features
✔ Scrapes event title, date, time, description, and URL
✔ Converts dates and times to a consistent format (YYYY-MM-DD, HH:MM 24h)
✔ Handles pagination and API rate limits
✔ Automatically uploads scraped events to WordPress
✔ Prevents duplicate event uploads

📂 Project Structure
Copy
Edit
📦 Sergiproject
 ┣ 📜 crawler.py            # Main script for posting in wordpress
 ┣ 📜 functions.py          # Aux script for functions and scrapping
 ┣ 📜 utilities.py          # Countriy jsons and different utilities  
 ┣ 📜 requirements.txt    # Python dependencies
 ┣ 📜 README.md           # Project documentation (this file)
 ┣ 📜 .env          # Configuration settings (API keys, URLs)
 ┗ 📂 chambers      # Scripts for the different chambers
🔧 Setup & Installation
1️⃣ Prerequisites
Ensure you have:

Python 3.9+
pip installed
2️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Configure Settings
Modify config.py with:

WordPress API credentials
API keys (if required)
Wordpress URL
🚀 Usage
Run the script:

bash
Copy
Edit
python main.py
It will:
✅ Scrape events from chamber websites
✅ Process event data
✅ Upload new events to WordPress

🛠️ Configuration Options
Modify .env to customize:

Event date filtering (e.g., scrape only future events)
Pagination handling
API request limits
📝 WordPress API Integration
The script interacts with the WordPress API to:

Fetch existing events (to avoid duplicates)
Upload new events
Delete outdated events
Example API call:

python
Copy
Edit
requests.post(
    "https://yourwordpresssite.com/wp-json/wp/v2/events",
    json=event_data,
    auth=(username, password),
)
📌 Future Improvements
🔹 Add multi-threading for faster scraping
🔹 Implement error handling & logging
🔹 Expand to more chambers

📜 License
This project is licensed under the MIT License.

🚀 Happy Scraping!
Let me know if you need modifications! 🚀