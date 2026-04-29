import sqlite3
from typing import runtime_checkable
from playwright.sync_api import sync_playwright
from datetime import datetime
import random
import json
import sys
import argparse
from tqdm import tqdm
import eel

@eel.expose
def set_scraper_var(name, value):
    globals()[name] = value

@eel.expose
def get_scraper_var(name):
    return globals()[name]



# so emojis don't break the script
sys.stdout.reconfigure(encoding='utf-8')

with open("settings.json", "r") as file:
    globals().update(json.load(file))

parser = argparse.ArgumentParser(
        description="These settings and more can be found in settings.json. Also check out README.md!"
                                 )

parser.add_argument("--purge-db", action="store_true", help="wipe the database of all listings")
parser.add_argument("--url", help="the facebook url to scrape")
parser.add_argument("--headless", action="store_true", help="run the browser without a window")
parser.add_argument("--windowed", action="store_true", help="run the browser in a window, like normal")
parser.add_argument("--scrolls", type=int, help="how many times the scraper should scroll down")

args = parser.parse_args()

if args.purge_db:
    PURGE_DB_ON_START = True

if args.url:
    FACEBOOK_URL = args.url

if args.headless and args.windowed:
    print("You can't run both headless and windowed at the same time lol")
    sys.exit(0)
if args.headless:
    RUN_HEADLESS = True
elif args.windowed:
    RUN_HEADLESS = False


if args.scrolls:
    SCROLLS = args.scrolls

category = "Unkown"

if "vehicles" in FACEBOOK_URL.lower():
    category = "Vehicle"

conn = sqlite3.connect("listings.db")
conn.execute('PRAGMA journal_mode=WAL;')

cursor = conn.cursor()

def init_db(): 

    if PURGE_DB_ON_START:
        cursor.execute('''
        DROP TABLE IF EXISTS listings

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
            scraped_date TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    print("database ready")
    eel.log("database ready")

def add_listing(title, price, url, location, metadata, img_url):
    metadata = json.dumps(metadata)
    try:
        # insert it into the db
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO listings (title, price, url, location, metadata, scraped_date, category, image_url)
            VALUES (?, ?, ?, ?, ?, ?,  ?, ?)
                       ''', (title, price, url, location, metadata, now, category, img_url))
        conn.commit()
    except sqlite3.IntegrityError:
        # update the current listing in the db
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                UPDATE listings set title = ?, price = ?, location = ?, metadata = ?, scraped_date = ?, category = ?, image_url = ? WHERE url = ?
                        ''', (title, price, location, metadata, now, category, img_url, url))
            conn.commit()
        except: 
            print(f"Could not add {title}")
            pass


def parse_data(listings):
    listings_found = 0
    for item in listings:
        listings_found += 1
        try:
            href = item.get_attribute("href", timeout=1000)
            img_url = item.locator("img").get_attribute("src", timeout=1000)
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

            tqdm.write(f"{title} | ${price} | {clean_url} ")
            eel.log(f"{title} | ${price} | {clean_url} ")

            add_listing(title, price, clean_url, location, raw_text, img_url)


        except Exception as e:
            print(f"Parse error for listing -> {e}")
            eel.log(f"Parse error for listing -> {e}")
            
    return listings_found


@eel.expose
def run_scraper():
    listings_found = 0

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
        eel.log("context launched!")

        page = browser_context.new_page()


        print("visiting marketplace")
        eel.log("visiting marketplace")
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

        pbar = tqdm(total=SCROLLS, desc="Scraping")

        # grab the first listings we see
        listings = page.locator('a[href*="/marketplace/item/"]').all()
        listings_found += parse_data(listings)

        # if the last listing is the same 3 times in a row, we've reached the end of the results.
        last_listing_same = 0
        last_listing = ""

        tqdm.write(f"scrolls: {SCROLLS}")
        eel.log(f"scrolls: {SCROLLS}")
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
                listings_found += parse_data(listings)
                if listings[-1] == last_listing:
                    last_listing_same += 1
                    if last_listing_same == 3:
                        print("reached the end of the results, exiting...")
                last_listing = listings[-1]

            pbar.update(1)

            stats = pbar.format_dict

            remaining = (stats['total'] - stats['n']) / stats['rate'] if stats['rate'] else 0
            eta_string = pbar.format_interval(remaining)
            try:
                eel.update_progress(i + 1, eta_string, listings_found)
            except:
                pass

        page.wait_for_timeout(2000)

        listings = page.locator('a[href*="/marketplace/item/"]').all()

        listings_found += parse_data(listings)
        pbar.close()

        tqdm.write("finished, exiting")
        eel.log("finished, exiting")
        eel.finished()
        browser_context.close()


if __name__ == "__main__":
    init_db()
    
    run_scraper()
