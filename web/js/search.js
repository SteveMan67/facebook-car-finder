async function search() {
  const listingsContainer = document.querySelector(".listings");
  listingsContainer.innerHTML = "";
  const listings = await eel.search()();
  console.log(listings);
  listings.forEach((listing) => {
    addListing(listing);
  });
}

search();

function addListing(listingData) {
  const listingsContainer = document.querySelector(".listings");
  const l = document.createElement("a");
  l.href = listingData.url;
  l.target = "_blank";
  l.classList.add("listing");
  console.log(listingData);
  const listingHtml = `
    <img
      src="${listingData.image_url}"
      alt=""
    />
    <p class="listing-title">${listingData.title}</p>
    <div class="price-mileage">
      <div class="price">
        <img src="icons/money.svg" alt="" />
        <p>${listingData.price.toLocaleString()}</p>
      </div>
      <div class="mileage">
        <img src="icons/mileage.svg" alt="" />
        <p>${listingData.mileage.toLocaleString()}</p>
      </div>
    </div>
    <div class="location">
      <img src="icons/location.svg" alt="" />
      <p>${listingData.location}</p>
    </div>
  `;

  l.innerHTML = listingHtml;

  listingsContainer.appendChild(l);
}

const category = document.getElementById("category");
const minPrice = document.getElementById("min-price");
const maxPrice = document.getElementById("max-price");
const minMileage = document.getElementById("min-mileage");
const maxMileage = document.getElementById("max-mileage");
const minYear = document.getElementById("min-year");
const maxYear = document.getElementById("max-year");

console.log(minMileage, maxMileage);

async function updateFilterInputs() {
  minPrice.value = await eel.get_var("MIN_PRICE")();
  maxPrice.value = await eel.get_var("MAX_PRICE")();
  minMileage.value = await eel.get_var("MIN_MILEAGE")();
  maxMileage.value = await eel.get_var("MAX_MILEAGE")();
  minYear.value = await eel.get_var("MIN_YEAR")();
  maxYear.value = await eel.get_var("MAX_YEAR")();
}

function addListener(pythonVar, element) {
  element.addEventListener("keydown", async (e) => {
    if (element.value !== "" && e.key === "Enter") {
      await eel.set_var(pythonVar, parseInt(element.value, 10));
      search();
    }
  });
  element.addEventListener("blur", async () => {
    if (element.value !== "") {
      await eel.set_var(pythonVar, parseInt(element.value, 10));
      search();
    }
  });
}

addListener("MIN_PRICE", minPrice);
addListener("MAX_PRICE", maxPrice);
addListener("MIN_MILEAGE", minMileage);
addListener("MAX_MILEAGE", maxMileage);
addListener("MIN_YEAR", minYear);
addListener("MAX_YEAR", maxYear);

updateFilterInputs();

// set up the model dropdown

makeInput = document.querySelector(".make input");
makeDropdown = document.querySelector(".make .dropdown");
modelInput = document.querySelector(".model input");
modelDropdown = document.querySelector(".model .dropdown");

let filteredMakes = [];
let filteredModels = [];
let modelsForMake = [];

function renderList(listElement, items, callback) {
  const html = items
    .map(
      (item, index) =>
        `<li class=${index == 0 ? "highlight" : ""} onclick="window['${callback.name}']('${item}')">${item}</li>`,
    )
    .join("");

  listElement.innerHTML = html;
  listElement.style.display = items.length ? "block" : "none";
}

function selectMake(make) {
  makeInput.value = make;
  makeDropdown.style.display = "none";

  modelInput.disabled = false;
  modelInput.focus();
  const makes = carBrands.find(
    (f) => f.brand.toLowerCase() === makeInput.value.toLowerCase(),
  );
  modelsForMake = makes.models;
  modelInput.value = "";
  renderList(modelDropdown, makes.models, (model) => {
    makeInput.value = model;
    modelDropdown.style.display = none;
  });
}

function selectModel(model) {
  modelInput.value = model;
  modelDropdown.style.display = "none";
}

makeInput.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  makeDropdown.innerHtml = "";

  if (query) {
    filteredMakes = carBrands.filter((f) =>
      f.brand.toLowerCase().startsWith(query),
    );

    const brandNames = filteredMakes.map((f) => f.brand);
    renderList(makeDropdown, brandNames, selectMake);
  } else {
    makeDropdown.style.display = "none";
  }
});

makeInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && filteredMakes.length) {
    selectMake(filteredMakes[0].brand);
  }
});

makeInput.addEventListener("mouseup", () => {
  makeInput.select();
});

makeInput.addEventListener("blur", () => {
  makeDropdown.style.display = "none";
});

modelInput.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  modelDropdown.innerHtml = "";

  if (query) {
    filteredModels = modelsForMake.filter((f) =>
      f.toLowerCase().startsWith(query),
    );
    renderList(modelDropdown, filteredModels, selectModel);
  } else {
    renderList(modelDropdown, modelsForMake, selectModel);
  }
});

modelInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && filteredModels.length) {
    selectModel(filteredModels[0]);
  }
});

modelInput.addEventListener("mouseup", () => {
  modelInput.select();
});

modelInput.addEventListener("blur", () => {
  modelDropdown.style.display = "none";
});
