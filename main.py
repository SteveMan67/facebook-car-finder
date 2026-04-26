import eel
import search
import scraper


@eel.expose
def unique_check():
    return "hello"

eel.init('web')
eel.start('search.html')
