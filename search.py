import sqlite3
from secrets import *
import smtplib
from email.message import EmailMessage
import json

with open("settings.json", "r") as file:
    globals().update(json.load(file))

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

listing_count = 0

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
        print(item)
        body += "---------------------------------\r"
        body += f"{item[0]}\n" # Title
        body += f"${item[1]}\n" # Price
        body += f"{item[2]}mi\n" # Mileage
        body += f"{item[5]}\n" # Location
        body += f"{item[3]}\n" # url

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
        if "K" in raw_mileage:
            mileage_str = raw_mileage.split("K")[0]
            mileage = int(float(mileage_str) * 1000)
        else:
            mileage = (''.join(filter(str.isdigit, raw_mileage)))

        out["mileage"] = mileage
    return out

for row in rows:
    data = get_data_from_row(row)
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
                        INSERT INTO viewed (url, title, price, mileage, year, location)
                        VALUES (?, ?, ?, ?, ?, ?)
                           ''', (row[3], row[0], row[1], row[2], row[4], row[5]))

            conn.commit()
            new_listings.append(row)
            print("!!! NEW !!!")
        except Exception as e:
            pass
        listing_count += 1
        print(row[0])
        print(f'${row[1]}')
        print(f'Mileage: {row[2]}')
        print(f'Location: {row[5]}')
        print(f'url: {row[3]}')

if len(new_listings) > 0 and SEND_NOTIFICATIONS:
    send_notification("New Listings Found", new_listings)

print("")
print(f"found {listing_count} total, {len(new_listings)} new listings matching search parameters")

input()
