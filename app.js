const TASK_KEYWORDS = new Set([
  "todo", "to-do", "buy", "call", "email", "submit", "finish", "pay", "schedule", "book", "fix"
]);

const REMINDER_KEYWORDS = new Set([
  "remind", "remember", "deadline", "meeting", "appointment", "tomorrow", "today", "tonight",
  "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]);

const STORE_KEY = "screenshot-replace-items";

const fileInput = document.getElementById("fileInput");
const fallbackText = document.getElementById("fallbackText");
const ingestBtn = document.getElementById("ingestBtn");
const clearBtn = document.getElementById("clearBtn");
const downloadBtn = document.getElementById("downloadBtn");
const statusEl = document.getElementById("status");
const itemList = document.getElementById("itemList");

function getItems() {
  const raw = localStorage.getItem(STORE_KEY);
  return raw ? JSON.parse(raw) : [];
}

function saveItems(items) {
  localStorage.setItem(STORE_KEY, JSON.stringify(items));
}

function cleanText(text) {
  const compact = (text || "").replace(/\s+/g, " ").trim();
  return compact || "Untitled capture";
}

function classify(text) {
  const tokens = new Set(text.toLowerCase().match(/[a-zA-Z-]+/g) || []);
  for (const token of tokens) {
    if (TASK_KEYWORDS.has(token)) return "task";
  }
  for (const token of tokens) {
    if (REMINDER_KEYWORDS.has(token)) return "reminder";
  }
  return "note";
}

function titleFrom(text, maxWords = 8) {
  const words = text.split(" ");
  const summary = words.slice(0, maxWords).join(" ");
  return words.length > maxWords ? `${summary}…` : summary;
}

function extractTimeHint(text) {
  const lowered = text.toLowerCase();
  const now = new Date();

  const at = (date, hour) => {
    const d = new Date(date);
    d.setHours(hour, 0, 0, 0);
    return d.toISOString();
  };

  if (lowered.includes("tomorrow")) {
    const d = new Date(now);
    d.setDate(d.getDate() + 1);
    return at(d, 9);
  }
  if (lowered.includes("today") || lowered.includes("tonight")) {
    return at(now, 18);
  }

  const weekdays = {
    monday: 1, tuesday: 2, wednesday: 3, thursday: 4, friday: 5, saturday: 6, sunday: 0
  };
  for (const [name, idx] of Object.entries(weekdays)) {
    if (lowered.includes(name)) {
      const d = new Date(now);
      let delta = (idx - d.getDay() + 7) % 7;
      if (delta === 0) delta = 7;
      d.setDate(d.getDate() + delta);
      return at(d, 9);
    }
  }
  return null;
}

async function extractTextFromImage(file) {
  if (!window.Tesseract) return "";
  const result = await Tesseract.recognize(file, "eng");
  return (result?.data?.text || "").trim();
}

function renderItems() {
  const items = getItems();
  itemList.innerHTML = "";

  if (!items.length) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = "No items yet. Ingest a screenshot above.";
    itemList.appendChild(li);
    return;
  }

  items.forEach((item, idx) => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${idx + 1}. [${item.kind}] ${item.title}</strong><br>
      <span>${item.body}</span><br>
      <small>reminder: ${item.reminder_at || "none"}</small><br>
      <small>source: ${item.source}</small>`;
    itemList.appendChild(li);
  });
}

function setStatus(message) {
  statusEl.textContent = message;
}

ingestBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    setStatus("Please choose a screenshot file first.");
    return;
  }

  ingestBtn.disabled = true;
  setStatus("Reading screenshot... (OCR can take a few seconds)");

  try {
    const ocrText = await extractTextFromImage(file);
    const extracted = ocrText || fallbackText.value.trim() || file.name.replace(/\.[^.]+$/, "").replace(/_/g, " ");
    const cleaned = cleanText(extracted);

    const item = {
      source: file.name,
      kind: classify(cleaned),
      title: titleFrom(cleaned),
      body: cleaned,
      reminder_at: extractTimeHint(cleaned),
      created_at: new Date().toISOString()
    };

    const items = getItems();
    items.push(item);
    saveItems(items);
    renderItems();

    setStatus(`Saved: [${item.kind}] ${item.title}`);
  } catch (err) {
    setStatus(`Could not read screenshot with OCR. Use fallback text. Error: ${String(err)}`);
  } finally {
    ingestBtn.disabled = false;
  }
});

clearBtn.addEventListener("click", () => {
  localStorage.removeItem(STORE_KEY);
  renderItems();
  setStatus("Cleared all saved items.");
});

downloadBtn.addEventListener("click", () => {
  const items = getItems();
  const blob = new Blob([JSON.stringify(items, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "captures.json";
  a.click();
  URL.revokeObjectURL(url);
});

renderItems();
