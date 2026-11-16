const messageBox = document.getElementById("message");
const results = document.getElementById("results");
const uploadForm = document.getElementById("upload-form");
const manualForm = document.getElementById("manual-form");

function showMessage(text, type = "error") {
  messageBox.textContent = text;
  messageBox.className = `message ${type}`;
  messageBox.hidden = false;
}

function clearMessage() {
  messageBox.hidden = true;
  messageBox.textContent = "";
}

function setBusy(button, busy, label) {
  if (!button) return;
  button.disabled = busy;
  button.textContent = busy ? "Working..." : label;
}

async function sendPrediction(formData, button, label) {
  clearMessage();
  setBusy(button, true, label);
  results.hidden = true;
  try {
    const response = await fetch("/predict", { method: "POST", body: formData });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "The server could not process the prediction.");
    renderResults(payload);
    showMessage("Prediction completed successfully.", "success");
  } catch (error) {
    showMessage(error.message || "The prediction failed. Please try again.");
  } finally {
    setBusy(button, false, label);
  }
}

function renderResults(payload) {
  const summary = document.getElementById("summary");
  summary.innerHTML = "";
  [["phishing", "Phishing"], ["legitimate", "Legitimate"], ["total", "Total"]].forEach(([key, label]) => {
    const card = document.createElement("div");
    card.className = "summary-card";
    card.innerHTML = `<strong>${payload.summary[key]}</strong><span>${label}</span>`;
    summary.appendChild(card);
  });

  const table = document.getElementById("results-table");
  table.innerHTML = "";
  const head = document.createElement("tr");
  payload.columns.forEach((column) => {
    const cell = document.createElement("th");
    cell.textContent = column;
    head.appendChild(cell);
  });
  table.appendChild(head);
  payload.rows.forEach((row) => {
    const line = document.createElement("tr");
    payload.columns.forEach((column) => {
      const cell = document.createElement("td");
      cell.textContent = row[column] ?? "";
      if (column === "prediction_label") {
        cell.className = row[column] === "Phishing" ? "label-phishing" : "label-legitimate";
      }
      line.appendChild(cell);
    });
    table.appendChild(line);
  });
  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    const uploadMode = tab.dataset.mode === "upload";
    uploadForm.hidden = !uploadMode;
    manualForm.hidden = uploadMode;
    clearMessage();
  });
});

const csvFile = document.getElementById("csv-file");
if (csvFile) {
  csvFile.addEventListener("change", () => {
    document.getElementById("file-name").textContent = csvFile.files[0]?.name || "No file selected";
  });
}

uploadForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!csvFile.files.length) {
    showMessage("Please select a CSV file first.");
    return;
  }
  const formData = new FormData();
  formData.append("file", csvFile.files[0]);
  sendPrediction(formData, uploadForm.querySelector("button"), "Predict CSV");
});

manualForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  const fields = [...manualForm.querySelectorAll("input[name]")];
  const header = fields.map((field) => field.name).join(",");
  const values = fields.map((field) => field.value).join(",");
  const blob = new Blob([`${header}\n${values}\n`], { type: "text/csv" });
  const formData = new FormData();
  formData.append("file", blob, "manual-entry.csv");
  sendPrediction(formData, manualForm.querySelector("button"), "Predict website");
});

document.getElementById("train-button")?.addEventListener("click", async (event) => {
  clearMessage();
  setBusy(event.currentTarget, true, "Train model");
  try {
    const response = await fetch("/train");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Training failed.");
    showMessage(payload.message || "Training completed successfully.", "success");
  } catch (error) {
    showMessage(error.message || "Training failed.");
  } finally {
    setBusy(event.currentTarget, false, "Train model");
  }
});
