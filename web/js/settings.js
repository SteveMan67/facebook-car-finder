const facebookUrl = document.getElementById("facebook-url");
const scrollsInput = document.getElementById("scrolls");
const signIn = document.getElementById("sign-in");
const signInText = signIn.querySelector("p");

const sendNotifications = document.getElementById("send-notifications");
const appPassword = document.getElementById("google-app-password");
const senderAddress = document.getElementById("sender-address");
const recieverAddress = document.getElementById("reciever-address");

async function updateValues() {
  facebookUrl.value = await eel.get_setup_var("FACEBOOK_URL")();
  scrollsInput.value = await eel.get_setup_var("SCROLLS")();
  sendNotifications.checked = await eel.get_setup_var("SEND_NOTIFICATIONS")();
  appPassword.value = await eel.get_setup_var("APP_PASSWORD")();
  senderAddress.value = await eel.get_setup_var("SENDER_ADDRESS")();
}

updateValues();

signIn.addEventListener("mouseup", async () => {
  signInText.innerText = "Opening chrome, please wait";
  await eel.sign_into_marketplace()();
  signInText.innerText = "Sign into Facebook";
});

async function addListener(pythonVar, el) {
  el.addEventListener("keydown", async (e) => {
    if ((e.key = "Enter")) {
      await eel.set_setup_var(pythonVar, el.value)();
      await eel.save_settings()();
    }
  });
  el.addEventListener("blur", async () => {
    await eel.set_setup_var(pythonVar, el.value)();
    await eel.save_settings()();
  });
}

addListener("FACEBOOK_URL", facebookUrl);
addListener("APP_PASSWORD", appPassword);

senderAddress.addEventListener("keydown", async (e) => {
  if ((e.key = "Enter" && isValidFormat(senderAddress))) {
    await eel.set_setup_var(pythonVar, senderAddress.value)();
    await eel.save_settings()();
  }
});

senderAddress.addEventListener("blur", async (e) => {
  if (isValidFormat(senderAddress)) {
    await eel.set_setup_var(pythonVar, senderAddress.value)();
    await eel.save_settings()();
  }
});

sendNotifications.addEventListener("mouseup", async (e) => {
  await eel.set_setup_var("SEND_NOTIFICATIONS", sendNotifications.checked)();
  await eel.save_settings()();
});

sendNotifications.addEventListener("blur", async () => {
  await eel.set_setup_var("SEND_NOTIFICATIONS", sendNotifications.checked)();
  await eel.save_settings()();
});

scrollsInput.addEventListener("keydown", async (e) => {
  if (e.key == "Enter") {
    await eel.set_setup_var("SCROLLS", scrollsInput.valueAsNumber)();
    await eel.save_settings()();
  }
});

scrollsInput.addEventListener("blur", async (e) => {
  await eel.set_setup_var("SCROLLS", scrollsInput.valueAsNumber)();
  await eel.save_settings()();
});

const emailPills = document.querySelector(".reciever-addresses .pills");

function addPill(pillText) {
  const div = document.createElement("div");
  div.classList.add("pill");
  div.innerHTML = `
    <p>${pillText}</p>
  `;
  const img = document.createElement("img");
  img.src = "icons/close.svg";
  div.appendChild(img);
  img.addEventListener("mouseup", () => {
    div.remove();
    savePills();
  });
  emailPills.appendChild(div);
}

function getPills() {
  const pillsElements = emailPills.querySelectorAll("p");
  out = [];
  pillsElements.forEach((el) => {
    out.push(el.innerText);
  });
  return out;
}

async function updateReceiverAddresses() {
  addresses = await eel.get_setup_var("RECIEVER_ADDRESSES")();
  addresses.forEach((address) => {
    addPill(address);
  });
}

updateReceiverAddresses();

function isValidFormat(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

async function savePills() {
  await eel.set_setup_var("RECIEVER_ADDRESSES", getPills())();
  await eel.save_settings();
}

recieverAddress.addEventListener("keypress", async (e) => {
  if (
    e.key == "Enter" &&
    recieverAddress.value !== "" &&
    isValidFormat(recieverAddress.value)
  ) {
    addPill(recieverAddress.value);
    recieverAddress.value = "";
    savePills();
  }
});

recieverAddress.addEventListener("blur", async () => {
  if (recieverAddress.value && isValidFormat(recieverAddress)) {
    addPill(recieverAddress.value);
    recieverAddress.value = "";
    savePills();
  }
});
