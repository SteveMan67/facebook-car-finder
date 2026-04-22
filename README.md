## Facebook Marketplace Scraper

This is a marketplace scraper built for searching for cars. I made it because the facebook marketplace filters are very broken. Also I'm looking for a car, you can probably tell which one by the default config in settings.py.

### **HOW IT WORKS**

`scraper.exe`. is for saving cars from marketplace into a database. It will open chrome, go to the url provided, and save all the cars it finds. By changing the url, you can filter it even more than you could in `settings.json`. For example, say I'm looking for a stickshift car in Dallas, I would go to facebook marketplace, apply those filters, then copy the url into `FACEBOOK_URL`. It's best not to apply too many filters as facebook marketplace is really bad about applying multiple filters at once.

Once you've scraped to your heart's content, you can filter those results with `search.py`. That searches through the database of cars that you've scraped and filters it down according to your `settings.json`.

---

### **Setting up the scraper**

Just run `setup.exe`. That walks you through setting up the scraper. If you wish to configure either the filters or other settings, documentation is below.

**Requirements:**

All the dependencies are build into the .exe files. You should only need chrome.

- Chrome or Chromium

## **Scraper Settings**

**`CHROME_PATH`**

The path to your chrome/chromium executable. On windows, this is typically `C:\Program Files\Google\Chrome\Application\chrome.exe`. If you use Linux you probably know how to find it.

`USER_PATH`

The path to the profile directory of the chrome profile you wish to use. If you set this to a non-chrome profile, chrome will just make a profile there.

`RUN_HEADLESS`

Choose whether chrome will run in a window or hidden (headless).

`FACEBOOK_URL`

Chooses the facebook page to scrape. I set it to search for stickshifts within 100 miles of tulsa. You can just go to facebook, apply the filters you want (assuming they work, which is not a given), copy that url and put it here.

`PURGE_DB_ON_START`

Chooses whether you want to erase the contents of the database when you run the scraper.

`SCROLLS`

How many times it should scroll the page down, by 1200-3000 pixels each time. The higher this number, the longer it will try to scroll. 50-100 is a good range, depending on how many search results you want to go through.

### **Actually, you know, running it**

Once you run the setup script and configure everything, you should be able to just run the python script either through the terminal (you probably use Linux if you choose this option) or by double clicking it.

It might take a few tries to get an instance of chrome running. I think it's something to do with the gpu. I also think I fixed it but I may be wrong.

It might take a minute or two to scrape, more if you set the `SCROLLS` to a ridiculously high number like I know you did. Once it's done it saves all the cars it found in the database.

---

### **Filtering with `search.py`**

Once you've scraped to your hearts content, you'll probably want to filter the results. That's what `search.py` is for. You can configure it with `setup.exe` or if you want a more advanced setup you can modify `settings.json`.

**Here are the options:**

`ALLOWED_MAKES`

A list of car brands to let through the filter. Anything else is tossed. If left blank it will let any make in SO MAKE SURE THAT DOESN'T HAPPEN! We wouldn't want any Cadillacs getting in now would we?

`ALLOWED_MODELS`

Same as above, but for car models. If left blank it will let any make in.

`EXCLUDED_TERMS`

A list of search terms. If a listing's title contains one of these, it will be filtered out.

`INCLUDED_TERMS`

If a listing contains **ANY** of these terms, it will be let through, Otherwise it will get filtered out.

`MAX_PRICE`
`MIN_PRICE`

The maximum and minimum prices to filter by (duh).

`MAX_MILEAGE`
`MIN_MILEAGE`

The minimum and maximum mileage to filter by (also duh).

`MIN_YEAR`
`MAX_YEAR`

The minimum and maximum year to filter by (double duh).

---

### **Setting Up Email Notifications**

The default configuration is for gmail, but you can use a different smtp server if you wish (untested). To set up gmail, you need to get your app password. You can find this in your google account settings. It should be a 16 character string. Put this in `secrets.py`. You can use the `example-secrets.py`, and just rename it.

**Like the scraper and search executables, this can be set up with `setup.exe`.**

`APP_PASSWORD` is your 16 character password used to connect to your email and send notifications.To find it, go to your google account settings and search for "app password". NOTE: 2fa has to be enabled to get the password.

`RECIEVER_ADDRESSES` is a list of email addresses to send the email to.

`SENDER_ADDRESS` is the email you got the app password for.

On windows, I used task scheduler to run a .bat file every day that points to the python files, in order. I also set `Run task as soon as possible if scheduled start is missed`. This is super useful for searching marketplace.

---

Have fun, don't do anything I wouldn't do!

## Testing for flavortown

Just download the most recent build for whatever platform your on, then run setup.exe to set everything up. After that just run the scraper and then the search file.
