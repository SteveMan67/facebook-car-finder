async function search() {
  const listings = await eel.search()();

  const listingsContainer = listings.forEach((l) => {});
}
search();

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
