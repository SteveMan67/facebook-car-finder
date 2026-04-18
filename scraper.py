import sqlite3
from playwright.sync_api import sync_playwright
from datetime import datetime
import random
import json

with open("settings.json", "r") as file:
    globals().update(json.load(file))

conn = sqlite3.connect("cars.db")
cursor = conn.cursor()

def init_db(): 

    if PURGE_DB_ON_START:
        cursor.execute('''
            DROP TABLE IF EXISTS cars 
                       ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER,
            url TEXT UNIQUE,
            year INTEGER,
            model TEXT,
            make TEXT,
            mileage INTEGER,
            location TEXT,
            scraped_date TEXT
        )
    ''')
    conn.commit()
    print("database ready")

def add_car(title, price, url, mileage, location, year=None):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO cars (title, price, url, year, mileage, location, scraped_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
                       ''', (title, price, url, year, mileage, location, now))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
        # car already exists in db
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                UPDATE cars set title = ?, price = ?, year = ?, mileage = ?, location = ?, scraped_date = ? WHERE url = ?
                        ''', (title, price, year, mileage, location, now, url))
            conn.commit()
        except: 
            print(f"Could not add {title}")
            pass

def parse_data(listings):
    for item in listings:
        href = item.get_attribute("href")
        clean_url = "https://facebook.com" + href.split("?")[0]

        raw_text = item.inner_text().split("\n")
        if (len(raw_text)) < 4:
            continue

        try:
            raw_price = raw_text[0]

            if raw_price == 'Free':
                price = 0
            else:
                price = int(raw_price.replace('$', '').replace(',', ''))

            shift = 1 if raw_text[1].startswith('$') else 0

            title = raw_text[1 + shift]
            location = raw_text[2 + shift]
            raw_mileage = raw_text[3 + shift] if len(raw_text) >= 4 + shift else 0

            if 'K' in raw_mileage:
                mileage_str = raw_mileage.split("K")[0]
                mileage = int(float(mileage_str) * 1000)
            else:
                mileage = int(''.join(filter(str.isdigit, raw_mileage)) or 0)

            year = title.split(" ")[0]

            print(f"{title} | ${price} | {mileage}mi | {clean_url} | {year}")

            add_car(title, price, clean_url, mileage, location, year)

        except Exception as e:
            print(f"Parse error: {raw_text} -> {e}")


def run_scraper():
    with sync_playwright() as p: 

        browser_context = None

        if RUN_HEADLESS:
            browser_context = p.chromium.launch_persistent_context(
                executable_path=CHROME_PATH,
                user_data_dir=USER_PATH,
                headless=True,
                )
        else:
            browser_context = p.chromium.launch_persistent_context(
                executable_path=CHROME_PATH,
                headless=False,
                user_data_dir=USER_PATH,
                )

        print("context launched!")

        page = browser_context.new_page()

        print("visiting marketplace")
        page.goto(FACEBOOK_URL)
        page.wait_for_selector('a[href*="/marketplace/item"]')
        page.wait_for_timeout(3000)

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
            if (i % 2 == 0):
                listings = page.locator('a[href*="/marketplace/item/"]').all()
                parse_data(listings)

        page.wait_for_timeout(2000)


        listings = page.locator('a[href*="/marketplace/item/"]').all()

        parse_data(listings)

        print("finished, exiting")
        browser_context.close()


if __name__ == "__main__":
    init_db()
    
    run_scraper()
