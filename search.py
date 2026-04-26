import sqlite3
from secrets import *
import smtplib
from email.message import EmailMessage
import json
import argparse
import eel

@eel.expose
def set_var(name, value):
    globals()[name] = value


with open("settings.json", "r") as file:
    globals().update(json.load(file))

parser = argparse.ArgumentParser(
        description="These settings and more can be found in settings.json. Also check out README.md!"
        )

parser.add_argument("--max-price", type=int, help="Maximum price")
parser.add_argument("--min-price", type=int, help="Minimum price")
parser.add_argument("--max-mileage", type=int, help="Maximum mileage (cars only)")
parser.add_argument("--min-mileage", type=int, help="Minimum mileage (cars only)")
parser.add_argument("--max-year", type=int, help="Maximum year (cars only)")
parser.add_argument("--min-year", type=int, help="Minimum year (cars only)")
parser.add_argument("--purge-viewed-db", action="store_true", help="Wipe the database of cars you've seen")
parser.add_argument("--send-notifications", action="store_true", help="Send_notifications")
parser.add_argument("--no-pause", action="store_true", help="Don't pause at the end")

args = parser.parse_args()

if args.max_price:
    MAX_PRICE = args.max_price

if args.min_price:
    MIN_PRICE = args.min_price

if args.max_mileage: 
    MAX_MILEAGE = args.max_mileage

if args.min_mileage:
    MIN_MILEAGE = args.min_mileage

if args.max_year:
    MAX_YEAR = args.max_year

if args.min_year:
    MIN_YEAR = args.min_year

if args.purge_viewed_db:
    PURGE_VIEWED_DB = True

if args.send_notifications:
    SEND_NOTIFICATIONS = True

conn = sqlite3.connect("listings.db")
cursor = conn.cursor()

cursor.execute('''SELECT title from listings where 1 = 1''')

conn.commit()

rows = cursor.fetchall()

print(f"db contains {len(rows)} rows")

if PURGE_VIEWED_DB:
    cursor.execute('''
                DROP TABLE IF EXISTS viewed
                   ''')
    conn.commit()

cursor.execute('''
                CREATE TABLE IF NOT EXISTS viewed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price INTEGER,
                    url TEXT UNIQUE,
                    location TEXT
                )
               ''')

cursor.execute('''SELECT title, price, url, location, category, metadata
               FROM listings 
               WHERE price <= ? AND price >= ?''', 
               (MAX_PRICE, MIN_PRICE))
conn.commit()

rows = cursor.fetchall()


new_listings = []

def send_notification(subject, new_items):
    sender = SENDER_ADDRESS
    pwd = APP_PASSWORD

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(RECIEVER_ADDRESSES)

    body = "New Listings found:\n\n"
    for item in new_items:
        body += "---------------------------------\r"
        body += f"{item['title']}\n" # Title
        body += f"${item['price']}\n" # Price
        body += f"{item['location']}\n" # Location
        if item['category'] == "Vehicle":
            body += f"{item['mileage']}mi\n" # Mileage
        body += f"{item['url']}\n" # url

    body += "---------------------------------\r"

    msg.set_content(body) 

    with smtplib.SMTP(SMTP_SERVER, PORT_NUMBER) as server:
        server.starttls()
        server.login(sender, pwd)
        server.send_message(msg)

def get_data_from_row(row):
    out = {}
    out["title"] = row[0]
    out["price"] = row[1]
    out["url"] = row[2]
    out["location"] = row[3]
    out["category"] = row[4]
    out["metadata"] = json.loads(row[5])

    if out["category"] == "Vehicle":
        metadata = out["metadata"]
        shift = 1 if metadata[1].startswith("$") else 0
        raw_mileage = metadata[3 + shift]
        mileage = 0
        if 'K' in raw_mileage:
            mileage_str = raw_mileage.split("K")[0]
            mileage = int(float(mileage_str) * 1000)
        elif 'M' in raw_mileage:
            mileage_str = raw_mileage.split("M")[0]
            mileage = int(float(mileage_str) * 1000000)
        else:
            mileage = (''.join(filter(str.isdigit, raw_mileage)))

        out["mileage"] = int(mileage)
    return out


@eel.expose
def search():
    out = []
    listing_count = 0
    for row in rows:
        try:
            data = get_data_from_row(row)
        except:
            continue
        filtered_make = False

        has_excluded_term = False

        for term in EXCLUDED_TERMS:
            has_excluded_term = True if term.lower() in data["title"].lower() or has_excluded_term else False

        has_included_terms = False

        if INCLUDED_TERMS == []:
            has_included_terms = True
        else:
            for term in INCLUDED_TERMS:
                has_included_terms = True if term.lower() in data["title"].lower() or has_included_terms else False

        has_second_included_term = False

        if INCLUDED_TERMS_TWO == []:
            has_second_included_term = True
        else:
            for term in INCLUDED_TERMS_TWO:
                has_second_included_term = True if term.lower() in data["title"].lower() or has_second_included_term else False

        passes_category = True

        if data["category"] == "Vehicle":
            passes_category = False

            correct_mileage = data["mileage"] >= MIN_MILEAGE and data["mileage"] <= MAX_MILEAGE

            year = int(data["title"].split(" ")[0])
            correct_year = year >= MIN_YEAR and year <= MAX_YEAR

            passes_category = correct_mileage and correct_year



        if not has_excluded_term and has_included_terms and has_second_included_term and passes_category:
            print("--------------------------------------")
            try:
                cursor.execute('''
                            INSERT INTO viewed (url, title, price, location)
                            VALUES (?, ?, ?, ?)
                            ''', (data["url"], data["title"], data["price"], data["location"]))

                conn.commit()
                new_listings.append(data)
                print("!!! NEW !!!")
            except:
                pass
            listing_count += 1
            print(row[0])
            print(f'${data["price"]}')
            print(f'Location: {data["location"]}')
            print(f'url: {data["url"]}')
            
            if data["category"] == "Vehicle":
                print(f'Mileage: {data["mileage"]}mi')

            out.append(data)
    return out

if __name__ == "__main__":
    listing_count = 0
    search()
    if len(new_listings) > 0 and SEND_NOTIFICATIONS:
        send_notification("New Listings Found", new_listings)

    print("")
    print(f"found {listing_count} total, {len(new_listings)} new listings matching search parameters")

    if not args.no_pause:
        input()
