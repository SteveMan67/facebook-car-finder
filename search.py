import sqlite3
from settings import *

db_path = r"C:\Users\Timothy\facebook-car-finder\cars.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''SELECT title from cars where 1 = 1''')

conn.commit() 

rows = cursor.fetchall()

print(f"db contains {len(rows)} rows")


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

matching_cars = []

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
            print("!!! NEW !!!")
            # TODO send email or notification for a new car
        except Exception as e:
            pass
        car_count += 1
        print(row[0])
        print(f'${row[1]}')
        print(f'Mileage: {row[2]}')
        print(f'Location: {row[5]}')
        print(f'url: {row[3]}')

print("")
print(f"found {car_count} cars matching search parameters")

