## Facebook Marketplace Scraper

This is a marketplace scraper built for searching for cars. I made it because the facebook marketplace filters are very broken. Also I'm looking for a car, you can probably tell which one by the default config in settings.py.

---

### **Setting up the scraper**

**Requirements:**

- Chrome
- Playwright - `pip install playwright`
- Python obviously

## **Setting up `settings.py`**

Note that file paths should start with r, like `r"C:\..."`. This is python's fault, not mine.

**`CHROME_PATH`**

First, find the path to chrome. On windows, this is typically `C:\Program Files\Google\Chrome\Application\chrome.exe`. If you use Linux you probably know how to find it.

**`DB_PATH`**

This is the path to the database file to store the cars in. It must point to an actual database file, even if it doesn't exist. If it doesn't exist, it will automatically create it.

`USER_PATH`

The path to the profile directory of the chrome profile you wish to use. The default should work globally, but you can also try

`RUN_HEADLESS`

Choose whether chrome will run in a window or hidden (headless). You will need to set this to false to sign in if using a temporary account.

`FACEBOOK_URL`

Chooses the facebook page to scrape. I set it to search for stickshifts within 100 miles of tulsa. You can just go to facebook, apply the filters you want (assuming the work, which is not a given), copy that url and put it here.

`PURGE_DB_ON_START`

Chooses whether you want to erase the contents of the database when you run the scraper.

`SCROLLS`

How many times it should scroll the page down, by 1200-3000 pixels each time. The higher this number, the longer it will try to scroll. 20-50 is a good number, though 50 may get into the dregs.

### **Actually, you know, running it**

Once you have all the settings right, you should be able to just run the python script either through the terminal (you probably use Linux if you choose this option) or by double clicking it.

It might take a minute or two to scrape. Once it's done it saves all the cars it found in the database.

---

### **Filtering with `search.py`**

Once you've scraped to your hearts content, you'll probably want to filter the results. That's what `search.py` is for. You'll also use `settings.py` to configure the search.

**Here are the options:**

`ALLOWED_MAKES`

A list of car brands to let through the filter. Anything else is tossed. If left blank it will let any make in SO MAKE SURE THAT DOESN'T HAPPEN! We wouldn't want any Cadillacs getting in now would we?

`ALLOWED_MODELS`

Same as above, but for car models. If left blank it will let any make in.

`EXCLUDED_TERMS`

A list of search terms. If a listing's title contains one of these, it will be filtered out.

`INCLUDED_TERMS`

If a listing contains **ANY** of these terms, it will be let through. Otherwise it will get filtered out.

`MAX_PRICE`
`MIN_PRICE`

The maximum and minimum prices to filter by (duh).

`MAX_MILEAGE`
`MIN_MILEAGE`

The minimum and maximum mileage to filter by.

`MIN_YEAR`
`MAX_YEAR`

The minimum and maximum year to filter by.

---

Have fun, don't do anything I wouldn't do!
