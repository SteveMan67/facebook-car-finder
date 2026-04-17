## Facebook Marketplace Scraper

This is a marketplace scraper built for searching for cars. I made it because the facebook marketplace filters are very broken. Also I'm looking for a car, you can probably tell which one by the default config in settings.py.

---

### **Setting up the scraper**

**Requirements:**

- Chrome
- Playwright - `pip install playwright`
- smtplib - if you want email notifications
- Python obviously

## **Setting up `settings.py`**

Note that file paths should start with r, like `r"C:\..."`. This is python's fault, not mine.

**`CHROME_PATH`**

First, find the path to chrome. On windows, this is typically `C:\Program Files\Google\Chrome\Application\chrome.exe`. If you use Linux you probably know how to find it.

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

It might take a few tries to get an instance of chrome running. Idk why, I was having trouble with it. If it doesn't work just try it Files\Google\Chrome\Application\chrome

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

### **Setting Up Email Notifications**

The default configuration is for gmail, but you can use a different smtp server if you wish. To set up gmail, you need to get your app password. You can find this in your google account settings. It should be a 16 character string. Put this in `secrets.py`. You can use the `example-secrets.py`, and just rename it.

You also need to set SENDER_ADDRESS to the email associated with the google account you created the app password for.

`RECIEVER_ADDRESSES` is a list of email addresses to send the email to.

On windows, I used task scheduler to run a .bat file every day that points to the python files, in order. I also set `Run task as soon as possible if scheduled start is missed`. This is super useful for searching marketplace.

---

Have fun, don't do anything I wouldn't do!

## Testing for flavortown

There are a lot of settings and a lot to set up. If you don't want to set all this up, I've included my database of cars. After that you can just run `search.py` and it should search the database. Do note that I searched for stickshift cars, so all the results will be stickshift. After that if you want to try to set up the scraper, go ahead. I've tried to make it as easy as possible.
