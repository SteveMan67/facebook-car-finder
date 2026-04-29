async function search() {
  const listingsContainer = document.querySelector(".listings");
  listingsContainer.innerHTML = "";
  const listings = await eel.search()();
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
  const listingHtml = `
    <img
      src="${listingData.image_url ? listingData.image_url : "icons/no-image.svg"}"
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

makePills = document.querySelector(".make .pills");
modelPills = document.querySelector(".model .pills");

async function updatePills() {
  const categoryOne = await eel.get_var("INCLUDED_TERMS")();
  const categoryTwo = await eel.get_var("INCLUDED_TERMS_TWO")();

  categoryOne.forEach((make) => {
    addPill(makePills, make, false);
  });

  categoryTwo.forEach((model) => {
    addPill(modelPills, model, false);
  });
}

updatePills();

async function updatePythonterms() {
  const categoryOne = getPills(makePills);
  const categoryTwo = getPills(modelPills);

  console.log(categoryOne, categoryTwo);

  await eel.set_var("INCLUDED_TERMS", categoryOne);
  await eel.set_var("INCLUDED_TERMS_TWO", categoryTwo);
  search();
}

const searchbar = document.getElementById("search");
const category = document.getElementById("category");
const minPrice = document.getElementById("min-price");
const maxPrice = document.getElementById("max-price");
const minMileage = document.getElementById("min-mileage");
const maxMileage = document.getElementById("max-mileage");
const minYear = document.getElementById("min-year");
const maxYear = document.getElementById("max-year");

searchbar.addEventListener("input", async () => {
  const listingsContainer = document.querySelector(".listings");
  listingsContainer.innerHTML = "";
  const listings = await eel.search_text(searchbar.value)();
  listings.forEach((listing) => {
    addListing(listing);
  });
});

async function addListener(pythonVar, element) {
  element.value = await eel.get_var(pythonVar)();
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

function addPill(pillsElement, name, update = true) {
  const p = document.createElement("p");
  p.innerText = name;
  const img = document.createElement("img");
  img.src = "icons/close.svg";
  img.addEventListener("mouseup", () => {
    // delete the element
    p.remove();
    updatePythonterms();
  });
  p.appendChild(img);
  pillsElement.appendChild(p);
  if (update) {
    updatePythonterms();
  }
}

function getPills(pillsElement) {
  pills = pillsElement.querySelectorAll("p");
  pList = [];
  pills.forEach((pill) => {
    pList.push(pill.innerText);
  });
  return pList;
}

function selectMake(make) {
  makeInput.value = "";
  if (!getPills(makePills).includes(make)) {
    addPill(makePills, make);
  }
  makeDropdown.style.display = "none";

  modelInput.disabled = false;
  modelInput.focus();
  const makes = carBrands.find((f) => f.brand === make);
  if (makes) {
    modelsForMake = makes.models;
    modelInput.value = "";
    renderList(modelDropdown, makes.models, (model) => {
      makeInput.value = model;
      modelDropdown.style.display = none;
    });
  }
}

function selectModel(model) {
  modelInput.value = "";
  if (!getPills(modelPills).includes(model)) addPill(modelPills, model);
  modelDropdown.style.display = "none";
}

function updateModelList() {
  makes = getPills(makePills);
  makes = makes.map((f) => f.toLowerCase());

  makeData = carBrands.filter((f) => makes.includes(f.brand.toLowerCase()));
  modelsForMake = [];
  makeData.forEach((make) => {
    make.models.forEach((model) => {
      modelsForMake.push(model);
    });
  });
}

makeInput.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  makeDropdown.innerHtml = "";

  if (query) {
    filteredMakes = carBrands.filter(
      (f) =>
        f.brand.toLowerCase().startsWith(query) &&
        !getPills(makePills).includes(f.brand),
    );

    const brandNames = filteredMakes.map((f) => f.brand);
    renderList(makeDropdown, brandNames, selectMake);
  } else {
    makeDropdown.style.display = "none";
  }
});

makeInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    if (filteredMakes[0]) {
      selectMake(filteredMakes[0].brand);
    } else {
      selectMake(makeInput.value);
    }
  }
});

makeInput.addEventListener("mouseup", () => {
  makeInput.select();
});

makeInput.addEventListener("blur", () => {
  makeDropdown.style.display = "none";
  if (makeInput.value) {
    selectMake(makeInput.value);
  }
});

modelInput.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  modelDropdown.innerHtml = "";
  updateModelList();

  if (query) {
    filteredModels = modelsForMake.filter(
      (f) =>
        f.toLowerCase().startsWith(query) && !getPills(modelPills).includes(f),
    );
    renderList(modelDropdown, filteredModels, selectModel);
  } else {
    renderList(modelDropdown, modelsForMake, selectModel);
  }
});

modelInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    if (filteredModels[0]) {
      selectModel(filteredModels[0]);
    } else {
      selectModel(modelInput.value);
    }
  }
});

modelInput.addEventListener("mouseup", () => {
  modelInput.select();
});

modelInput.addEventListener("blur", () => {
  modelDropdown.style.display = "none";
});
