import sqlite3
from secrets import *
import smtplib
from email.message import EmailMessage
import json

with open("settings.json", "r") as file:
    globals().update(json.load(file))

conn = sqlite3.connect("cars.db")
cursor = conn.cursor()

cursor.execute('''SELECT title from cars where 1 = 1''')

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
                    mileage INTEGER,
                    year INTEGER,
                    location TEXT
                )
               ''')

cursor.execute('''SELECT title, price, mileage, url, year, location
               FROM cars 
               WHERE price <= ? AND price >= ? AND mileage <= ? AND mileage >= ? AND year <= ? AND year >= ?''', 
               (MAX_PRICE, MIN_PRICE, MAX_MILEAGE, MIN_MILEAGE, MAX_YEAR, MIN_YEAR))
conn.commit()

rows = cursor.fetchall()

car_count = 0

new_cars = []

def send_notification(subject, new_items):
    sender = SENDER_ADDRESS
    pwd = APP_PASSWORD

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(RECIEVER_ADDRESSES)

    body = "New cars found:\n\n"
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

for row in rows:
    filtered_make = False

    if ALLOWED_MAKES == []:
        filtered_make = True
    
    for make in ALLOWED_MAKES:
        filtered_make = True if make.lower() in row[0].lower() or filtered_make else False

    filtered_model = False

    if ALLOWED_MODELS == []:
        filtered_model = True

    for model in ALLOWED_MODELS:
        filtered_model = True if model.lower() in row[0].lower() or filtered_model else False

    has_excluded_term = False

    for term in EXCLUDED_TERMS:
        has_excluded_term = True if term.lower() in row[0].lower() or has_excluded_term else False

    has_included_terms = False

    if INCLUDED_TERMS == []:
        has_included_terms = True
    else:
        for term in INCLUDED_TERMS:
            has_included_terms = True if term.lower() in row[0].lower() or has_included_terms else False


    if filtered_make and filtered_model and not has_excluded_term and has_included_terms:
        print("--------------------------------------")
        try:
            cursor.execute('''
                        INSERT INTO viewed (url, title, price, mileage, year, location)
                        VALUES (?, ?, ?, ?, ?, ?)
                           ''', (row[3], row[0], row[1], row[2], row[4], row[5]))

            conn.commit()
            new_cars.append(row)
            print("!!! NEW !!!")
        except Exception as e:
            pass
        car_count += 1
        print(row[0])
        print(f'${row[1]}')
        print(f'Mileage: {row[2]}')
        print(f'Location: {row[5]}')
        print(f'url: {row[3]}')

if len(new_cars) > 0 and SEND_NOTIFICATIONS:
    send_notification("New Car Listings", new_cars)

print("")
print(f"found {car_count} total, {len(new_cars)} new cars matching search parameters")

# send_notification("New Car Listings", [["1902 Rick Astley", 100, -2000, "platformed.jmeow.net", 1902, "Old England"]])

input()

