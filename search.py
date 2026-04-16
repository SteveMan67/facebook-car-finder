import sqlite3
from settings import *

db_path = r"C:\Users\Timothy\facebook-car-finder\cars.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''SELECT title from cars where 1 = 1''')

conn.commit() 

rows = cursor.fetchall()

print(f"db contains {len(rows)} rows")

cursor.execute('''SELECT title, price, mileage, url, year, location
               FROM cars 
               WHERE price <= ? AND price >= ? AND mileage <= ? AND mileage >= ? AND year <= ? AND year >= ?''', 
               (MAX_PRICE, MIN_PRICE, MAX_MILEAGE, MIN_MILEAGE, MAX_YEAR, MIN_YEAR))
conn.commit()

rows = cursor.fetchall()

car_count = 0

print(ALLOWED_MAKES)

for row in rows:
    filtered_make = False
    
    for make in ALLOWED_MAKES:
        filtered_make = True if make.lower() in row[0].lower() or filtered_make else False

    filtered_model = False

    for model in ALLOWED_MODELS:
        filtered_model = True if model.lower() in row[0].lower() or filtered_model else False

    has_excluded_term = False

    for term in EXCLUDED_TERMS:
        has_excluded_term = True if term.lower() in row[0].lower() or has_excluded_term else False

    if filtered_make and filtered_model and not has_excluded_term:
        car_count += 1
        print("--------------------------------------")
        print(row[0])
        print(f'${row[1]}')
        print(f'Mileage: {row[2]}')
        print(f'Location: {row[5]}')
        print(f'url: {row[3]}')

print("")
print(f"found {car_count} cars matching search parameters")

