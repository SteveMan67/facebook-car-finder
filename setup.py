import sys
import os
import shutil
import json
from tkinter import filedialog
from playwright.sync_api import sync_playwright
# Provides an easy way to setup the scraper
print("--- EASY SCRAPER SETUP ---")

template = "settings.example.json"
filename = "settings.json"

def get_os():
    if sys.platform == "win32":
        print("System: Windows")
        return "win"
    elif sys.platform == "darwin":
        print("System: MacOS")
        return "macos"
    else:
        print("System: Linux")
        return "linux"

def get_chrome_path(system):
    if system == "win":
        paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%localAppData%\Google\Chrome\Application\chrome.exe")
                ]
        for p in paths:
            if (os.path.exists(p)):
                return p
    elif system == "macos":
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path
    else:
        for app in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
            path = shutil.which(app)
            if path: return path
    return None

def get_user_data_dir(system):
    if system == "win":
        return os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    elif system == "macos":
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    else:
        return os.path.expanduser("~/.config/google-chrome")

def get_profiles(system):
    data_dir = get_user_data_dir(system)
    profiles = {}

    if not os.path.exists(data_dir):
        return profiles, data_dir
    
    for folder in os.listdir(data_dir):
        prefs_path = os.path.join(data_dir, folder, "Preferences")
        if os.path.exists(prefs_path):
            try:
                with open(prefs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("profile", {}).get("name", folder)
                    profiles[folder] = name
            except:
                pass
    return profiles, data_dir

def create_temp_dir(system):
    if system == "win":
        base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    elif system == "macos":
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:
        base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))

    app_dir = os.path.join(base_dir, "ScraperProfile")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_profile_path(system):
    profiles, data_dir = get_profiles(system)
    if not data["USER_PATH"] and input("Use existing setting? (y/n): ") == "y":
        return data["USER_PATH"]

    if len(profiles) == 0 or not os.path.exists(data_dir):
        # No user profiles found, ask to create temporary directory
        print("error finding user profiles")
        user_temp = input("Automatically create temporary directory? (y/n): ")
        if user_temp.lower() == "y":
            return create_temp_dir(system)
        else:
            if input("Use custom path? (y/n): "):
                return input("Enter Custom Path: ")
            else:
                print("Skipping USER_PATH")
    else:
        idx = 1
        dirs = []

        print("WARNING: Using an existing profile may lead to issues with the lock file, using a new profile is reccomended")

        print("0: [Create New Profile]")

        for dir_name, display_name in profiles.items():
            print(f"{idx}: {display_name} ({dir_name})")
            dirs.append(dir_name)
            idx += 1
        
        choice = input("Select Profile (num): ")
        if choice == "0":
            selected_path = os.path.join(data_dir, "ScraperProfile")
            return selected_path
        else:
            dir_name = dirs[int(choice) - 1]
            selected_path = os.path.join(data_dir, dir_name)
            print(f"Using: {selected_path}")
            return selected_path

# create the settings.json file from settings.template.json if it doesn't exist
if os.path.exists(template) and not os.path.exists(filename):
    shutil.copy(template, filename)
    print("Created settings.json file from template")

with open(filename, "r") as f:
    data = json.load(f)

while True:
    setup_id = input("What would you like to set up? (f)ilters, (s)craper, (e)mail, or (q)uit: ")

    if setup_id == "f":
        # Filter setup
        print("--- Filter Setup ---")
        print("-------------------------------")
        print("ALLOWED_MAKES is a list of car brands to let through. ")
        print("It is case insensitive.")

        makes = []

        list_item = input("Enter a make or (q) to quit: ")
        if not list_item.lower() == "q":
            makes.append(list_item)


        while not list_item.lower() == "q":
            list_item = input("Enter a make or (q) to quit: ")
            makes.append(list_item)

        data["ALLOWED_MAKES"] = makes
        
        print("-------------------------------")
        print("ALLOWED_MODELS is a list of car brands to let through. ")
        print("It is case insensitive.")

        models = []

        list_item = input("Enter a model or (q) to quit: ")
        if not list_item.lower() == "q":
            models.append(list_item)


        while not list_item.lower() == "q":
            list_item = input("Enter a make or (q) to quit: ")
            models.append(list_item)

        data["ALLOWED_MODELS"] = models

        print("-------------------------------")
        print("EXCLUDED_TERMS is a list of terms to exclude")
        print("If the title of a listing contains one of the items in the list, it will be filtered out.")
        print("It is (also) case insensitive.")

        exclude = []

        list_item = input("Enter a model or (q) to quit: ")
        if not list_item.lower() == "q":
            exclude.append(list_item)


        while not list_item.lower() == "q":
            list_item = input("Enter a make or (q) to quit: ")
            exclude.append(list_item)

        data["EXCLUDED_TERMS"] = models

        print("-------------------------------")
        data["MAX_PRICE"] = input("Enter the maxiumum price: ")
        print("-------------------------------")
        data["MIN_PRICE"] = input("Enter the minimum price: ")
        print("-------------------------------")
        data["MAX_MILEAGE"] = input("Enter the maximum mileage: ")
        print("-------------------------------")
        data["MIN_MILEAGE"] = input("Enter the minimum mileage: ")
        print("-------------------------------")
        data["MIN_YEAR"] = input("Enter the minimum year: ")
        print("-------------------------------")
        data["MAX_YEAR"] = input("Enter the maximum year: ")
        print("-------------------------------")

    elif setup_id == "s":
        # scraper setup
        print("--- Scraper Setup ---")
        print("-------------------------------")
        print("Getting OS")
        system = get_os()
        print("Attempting to find chrome path")
        path = get_chrome_path(system)
        if path == None:
            print("Chrome not found")
            print("Either install chrome or enter the path to a seperate browser (untested)")
            if input("Use custom path? (y/n) ") == "y":
                data["CHROME_PATH"] = input("Enter custom path: ")
            else:
                print("Skipping chrome path")

            if not data["USER_PATH"]:
                print("-------------------------------")
                print("USER_PATH chooses what chrome profile to use")
                data["USER_PATH"] = input("Enter custom chrome profile path: ")

        else:
            data["CHROME_PATH"] = path
            print(f"Using directory {path}")
            print("-------------------------------")
            print("USER_PATH chooses what chrome profile to use")
            data["USER_PATH"] = get_profile_path(system)
            print(f"Using directory {data['USER_PATH']}")

        print("-------------------------------")
        print("SCROLLS is the number of times the scraper will scroll down the page")
        print("Roughly 20-50 is a good number")

        data["SCROLLS"] = int(input("Input number of scrolls: "))

        print("-------------------------------")
        print("PURGE_DB_ON_START determines whether or not to clear the database of cars every time we scrape.")

        wipe_db = input("Wipe the database on start? (y/n): ")
        
        if wipe_db.lower() == "y":
            data["PURGE_DB_ON_START"] = True
        else:
            data["PURGE_DB_ON_START"] = False

        print("-------------------------------")
        print("FACEBOOK_URL is the url that the scraper will go to in order to find cars.")
        print("If you want to filter the search results more or only search within a specific radius, go to marketplace and apply those filters, then just copy the url here.")
        print("It is highly reccomended to do this as this is how you will get cars for your location.")

        skip = input("Skip? (y/n): ")

        if skip.lower() == "y":
            print("skipping url (be sure to make sure it's valid)")
        else:
            data["FACEBOOK_URL"] = input("Enter the url here: ")

        # Now we need to open that chrome profile so they can log into facebook
        print("-------------------------------")
        input("A chrome instance will open, please sign into marketplace there. (press enter) ")

        tries = 0
        max_tries = 5
        successful = False

        while tries < max_tries and not successful:
            with sync_playwright() as p:
                try:
                    browser_context = p.chromium.launch_persistent_context(
                        executable_path=data["CHROME_PATH"],
                        user_data_dir=data["USER_PATH"],
                        headless=False,
                        )
                    
                    print("Context launched!")

                    page = browser_context.new_page()
                    page.goto("https://www.facebook.com")
                    successful = True

                    browser_context.wait_for_event("close", timeout=0)

                except Exception as e:
                    print(e)
                    tries += 1
        if not successful:
            print(f"Opening Chrome failed after {max_tries} tries")


    elif setup_id == "e":
        # Email setup
        print("--- Email Setup ---")
        print("-------------------------------")
        print("In order to send emails, you need a gmail account and the app password from that account.")
        print("This is different than the password you use to sign in. ")
        print("In order to get it, go to your google account settings and search for 'App Password'")
        print("2fa has to be on.")
        print("It should be a 16 digit string with spaces between every 4 characters.")

        data["APP_PASSWORD"] = input("Enter it here: ")

        print("-------------------------------")
        data["SENDER_ADDRESS"] = input("Enter the email that the app password is from: ")

        print("-------------------------------")
        print("RECIEVER_ADDRESS is a list of all the addresses to send the new items to.")

        emails = []

        list_item = input("Enter an email or (q) to quit: ")
        if not list_item.lower() == "q":
            emails.append(list_item)


        while not list_item.lower() == "q":
            list_item = input("Enter a make or (q) to quit: ")
            emails.append(list_item)

        data["SENDER_ADDRESS"] = emails

 
    elif setup_id == "q":
        print("exiting...")
        break
    else:
        print("invalid option")

print("Saving to settings.json...")

with open(filename, "w") as f:
    json.dump(data, f, indent=4)

print("You're all set! Have a nice day.")
