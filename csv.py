from random import paretovariate
import sqlite3
import csv
import json

conn = sqlite3.connect("listings.db")
cursor = conn.cursor()

cursor.execute('''
            SELECT * FROM listings
               ''')

conn.commit()

rows = cursor.fetchall()

def parse_metadata(meta_str):
    metadata = json.loads(meta_str)
    
    year = 0
    milage = 0
    price = 0
    
    shift = 1 if metadata[1].startswith("$") else 0
    raw_mileage = "0"

    try:
        raw_mileage = metadata[3 + shift]
    except:
        pass

    if 'K' in raw_mileage:
        mileage_str = raw_mileage.split("K")[0]
        mileage = int(float(mileage_str) * 1000)
    elif 'M' in raw_mileage:
        mileage_str = raw_mileage.split("M")[0]
        mileage = int(float(mileage_str) * 1000000)
    else:
        mileage = (''.join(filter(str.isdigit, raw_mileage)))

    price = (''.join(filter(str.isdigit, metadata[0])))

    title = metadata[1 + shift]

    year = title.split(" ")[0]
    
    return year, mileage, price

with open("export.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    headers = [description[0] for description in cursor.description]
    headers = list(headers) + ["year", "mileage", "price"]
    writer.writerow(headers)

    for row in rows:
        db_id, title, price, url, category, metadata, location, scraped_date = row
        
        year, mileage, price = parse_metadata(metadata)


        new_row = list(row) + [year, mileage, price]
        writer.writerow(new_row)

conn.close()
print("done!")
