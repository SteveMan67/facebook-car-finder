# -- SEARCH SETUP --

# case insensitive
ALLOWED_MAKES = ['honda', 'acura']
ALLOWED_MODELS = ['accord', 'civic', 'tl', 'tsx']

# listings with any of these terms in their title will be ignored.
# You can also use this to filter out makes or models you don't want.
EXCLUDED_TERMS = ['2D']

# only show listings with one or more of these words
INCLUDED_TERMS = []

MAX_PRICE = 13500
MIN_PRICE = 0
MAX_MILEAGE = 200000
MIN_MILEAGE = 50000
MIN_YEAR = 2010
MAX_YEAR = 2022

# -- SCRAPER SETUP --

# Purge the database when the scraper runs (not reccomended)
PURGE_DB_ON_START = False

# example: r"C:\Users\yournamehere\facebook-car-finder\cars.db"
# this must point to a database, if it doesn't exist it will automatically make it.
DB_PATH = r"C:\Users\Timothy\facebook-car-finder\cars.db"

# you can use this to apply other filters
# Here I've set the search radius to tulsa and searched for manual transmissions.
# You can just copy the url directly from the browser, that's probably the easiest.
FACEBOOK_URL = "https://www.facebook.com/marketplace/tulsa/search?transmissionType=manual&query=Vehicles&category_id=546583916084032&exact=false&referral_ui_component=category_menu_item"

# determines what chrome profile directory to start in
# It's best to use a temporary account since it can lock the profile and not work if you don't
USER_PATH = r'C:\Temp\ChromeScraper'

# Path to your chrome executable
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# defines how many times the scraper will scroll down, 1200-3000 pixels at a time.
SCROLLS = 20

RUN_HEADLESS = True

