import sqlite3
from playwright.sync_api import sync_playwright
from datetime import datetime
import random
import json
import sys



# so emojis don't break the script
sys.stdout.reconfigure(encoding='utf-8')

with open("settings.json", "r") as file:
    globals().update(json.load(file))

category = "Unkown"

if "vehicles" in FACEBOOK_URL.lower():
    category = "Vehicle"

conn = sqlite3.connect("listings.db")
cursor = conn.cursor()

def init_db(): 

    cursor.execute('''
        DROP TABLE IF EXISTS cars;
                    ''')

    cursor.execute('''
        DROP TABLE IF EXISTS listings;
                    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER,
            url TEXT UNIQUE,
            category TEXT NOT NULL,
            metadata TEXT,
            location TEXT,
            scraped_date TEXT
        )
    ''')
    conn.commit()
    print("database ready")

def add_listing(title, price, url, location, metadata):
    metadata = json.dumps(metadata)
    try:
        # insert it into the db
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO listings (title, price, url, location, metadata, scraped_date, category)
            VALUES (?, ?, ?, ?, ?, ?,  ?)
                       ''', (title, price, url, location, metadata, now, category))
        conn.commit()
    except sqlite3.IntegrityError:
        # update the current listing in the db
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                UPDATE listings set title = ?, price = ?, location = ?, metadata = ?, scraped_date = ?, category = ? WHERE url = ?
                        ''', (title, price, location, metadata, now, url, category))
            conn.commit()
        except: 
            print(f"Could not add {title}")
            pass

def parse_data(listings):
    for item in listings:
        try:
            href = item.get_attribute("href", timeout=1000)
            clean_url = "https://facebook.com" + href.split("?")[0]

            raw_text = item.inner_text().split("\n")
            if (len(raw_text)) < 4:
                continue

            raw_price = raw_text[0]

            if raw_price == 'Free':
                price = 0
            else:
                price = int(raw_price.replace('$', '').replace(',', ''))

            shift = 1 if raw_text[1].startswith('$') else 0

            title = raw_text[1 + shift]
            location = raw_text[2 + shift]

            print(f"{title} | ${price} | {clean_url} ")

            add_listing(title, price, clean_url, location, raw_text)

        except Exception as e:
            print(f"Parse error for listing -> {e}")


def run_scraper():
    with sync_playwright() as p:

        # browser context only opens sometimes, try 15 times to open it

        tries = 0
        sucess = False

        while tries < 15 and not sucess:
            try:
                if RUN_HEADLESS:
                    browser_context = p.chromium.launch_persistent_context(
                        executable_path=CHROME_PATH,
                        user_data_dir=USER_PATH,
                        headless=True,
                        args=["--disable-gpu"]
                        )
                else:
                    browser_context = p.chromium.launch_persistent_context(
                        executable_path=CHROME_PATH,
                        headless=False,
                        user_data_dir=USER_PATH,
                        args=["--disable-gpu"]
                        )

                sucess = True
            except: 
                tries += 1

        print("context launched!")

        page = browser_context.new_page()


        print("visiting marketplace")
        page.goto(FACEBOOK_URL)
        try: 
            page.wait_for_selector('a[href*="/marketplace/item"]')
        except:
            print("Error getting page listings")
            print('Try setting "HEADLESS": false in settings.json. ')
            print('There may be a CAPTCHA or something else in the way.')
            input('Press any key to exit.')

            sys.exit(0)
            
        page.wait_for_timeout(3000)

        client = page.context.new_cdp_session(page)
        client.send("Emulation.setDeviceMetricsOverride", {
            "width": 1920,
            "height": 1080,
            "deviceScaleFactor": 0.5,
            "mobile": False,
            })

        # grab the first listings we see
        listings = page.locator('a[href*="/marketplace/item/"]').all()
        parse_data(listings)

        for i in range(SCROLLS):
            total_scroll = random.randint(2000, 5000)
            scrolled = 0

            while scrolled < total_scroll:
                chunk = random.randint(50, 100)
                page.evaluate(f"window.scrollBy({{top: {chunk}, left: 0, behavior: 'smooth'}})")
                scrolled += chunk
                page.wait_for_timeout(random.randint(10,50))

            page.wait_for_timeout(random.randint(500, 2000))

            # randomly scroll back up
            if random.random() < 0.1:
                back_chunk = random.randint(100, 300)
                page.evaluate(f"window.scrollBy({{top: -{back_chunk}, left: 0, behavior: 'smooth'}})")
                page.wait_for_timeout(random.randint(500, 1500))

            # grab listings every two scrolls to make sure we don't miss any if they get deleted
            if i % 2 == 0:
                listings = page.locator('a[href*="/marketplace/item/"]').all()
                parse_data(listings)
            print(f"--- PROGRESS: {i}/{SCROLLS} ---")

        page.wait_for_timeout(2000)


        listings = page.locator('a[href*="/marketplace/item/"]').all()

        parse_data(listings)

        print("finished, exiting")
        browser_context.close()


if __name__ == "__main__":
    init_db()
    
    run_scraper()
