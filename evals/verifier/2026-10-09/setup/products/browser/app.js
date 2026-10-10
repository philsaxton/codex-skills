const KEY = "receipt-preferences";
const checkbox = document.getElementById("email-receipts");
const preview = document.getElementById("preview");
const status = document.getElementById("status");
let saved = { emailReceipts: false };
try {
  const stored = JSON.parse(localStorage.getItem(KEY));
  if (stored && typeof stored.emailReceipts === "boolean") saved = stored;
} catch (_) {
  // Use defaults if there is no readable saved preference.
}

function render() {
  checkbox.checked = saved.emailReceipts;
  preview.textContent = `Email receipts: ${saved.emailReceipts ? "On" : "Off"}`;
}

document.getElementById("save").addEventListener("click", () => {
  saved = { emailReceipts: checkbox.checked };
  localStorage.setItem(KEY, JSON.stringify(saved));
  render();
  status.textContent = "Preferences saved.";
});

document.getElementById("cancel").addEventListener("click", () => {
  render();
  status.textContent = "Changes discarded.";
});

document.getElementById("defaults").addEventListener("click", () => {
  saved = { emailReceipts: false };
  localStorage.setItem(KEY, JSON.stringify(saved));
  render();
  status.textContent = "Defaults restored.";
});

render();
