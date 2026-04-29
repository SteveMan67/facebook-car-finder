const scrapeOptions = document.querySelector(".scrape-options");
const scraping = document.querySelector(".scraping");

const facebookUrl = document.getElementById("facebook-url");
const category = document.getElementById("category-input");
const scrollsInput = document.getElementById("scrolls-input");

const startScraper = document.getElementById("start-scraper");

const currentScrolls = document.getElementById("scrolls-current");
const scrollsTotal = document.getElementById("scrolls-total");
const timeRemaining = document.getElementById("time-remaining");
const progressBar = document.querySelector(".progress-bar");
const listingsFound = document.getElementById("listings-found");
const listingsPerScroll = document.getElementById("listings-per-scroll");

const output = document.querySelector(".output");

let scrolls = 0;
let totalScrolls = 100;

async function updateSettings() {
  facebookUrl.value = await eel.get_scraper_var("FACEBOOK_URL")();
  category.value = await eel.get_scraper_var("CATEGORY")();
  scrollsInput.value = await eel.get_scraper_var("SCROLLS")();
}

updateSettings();

startScraper.addEventListener("mouseup", async () => {
  if (facebookUrl.value) {
    await eel.set_scraper_var("FACEBOOK-URL", facebookUrl.value);
  }

  if (category.value) {
    await eel.set_scraper_var("CATEGORY", category.value);
  }

  if (scrollsInput.value) {
    await eel.set_scraper_var("SCROLLS", Number(scrollsInput.value));
  }

  scrapeOptions.classList.add("hidden");
  scraping.classList.remove("hidden");

  progressBar.style.setProperty("--percent", "0%");

  totalScrolls = await eel.get_scraper_var("SCROLLS")();
  scrollsTotal.innerText = totalScrolls;
  currentScrolls.innerText = "0";
  eel.run_scraper()();
});

function update_progress(scrolls, etaString, totalFound) {
  const percentDone = (scrolls / totalScrolls) * 100;
  progressBar.style.setProperty("--percent", `${percentDone}%`);
  currentScrolls.innerText = scrolls;
  timeRemaining.innerText = etaString;
  listingsFound.innerText = totalFound;
  listingsPerScroll.innerText = `${Math.round(totalFound / scrolls)}`;
}

eel.expose(update_progress);

function finished() {
  window.location.href = "http://localhost:8000/search.html";
}

function log(message) {
  output.textContent += message + "\n";
  output.scrollTop = output.scrollHeight;
}

eel.expose(log);

eel.expose(finished);
