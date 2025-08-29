// =============== Low-latency success sound (Web Audio) ===============
let dingCtx, dingBuffer, dingReady = false;

async function loadDing(url) {
  try {
    dingCtx = new (window.AudioContext || window.webkitAudioContext)();

    const unlock = () => {
      if (dingCtx && dingCtx.state === "suspended") {
        dingCtx.resume().catch(() => {});
      }
      window.removeEventListener("click", unlock);
      window.removeEventListener("touchstart", unlock);
      window.removeEventListener("keydown", unlock);
    };
    window.addEventListener("click", unlock, { once: true });
    window.addEventListener("touchstart", unlock, { once: true });
    window.addEventListener("keydown", unlock, { once: true });

    const res = await fetch(url, { cache: "force-cache" });
    const arr = await res.arrayBuffer();
    // decode may be async; await ensures it's ready
    dingBuffer = await dingCtx.decodeAudioData(arr);
    dingReady = true;
  } catch (e) {
    console.warn("Ding preload failed; will fall back to <audio>.", e);
    dingReady = false;
  }
}

/**
 * Play the ding and resolve when playback has STARTED.
 * - WebAudio: starts immediately; resolve on next tick
 * - <audio>: wait for play() Promise to resolve (started) or fail
 */
function playDingAsync() {
  return new Promise((resolve) => {
    if (dingReady && dingCtx && dingBuffer) {
      try {
        const src = dingCtx.createBufferSource();
        src.buffer = dingBuffer;
        src.connect(dingCtx.destination);
        src.start(0);
        // Resolve next tick to ensure start
        setTimeout(resolve, 0);
        return;
      } catch (_) {
        // fall through to <audio> fallback
      }
    }
    const el = document.getElementById("success-sound");
    if (el) {
      el.currentTime = 0;
      const p = el.play();
      if (p && typeof p.then === "function") {
        p.then(() => resolve()).catch(() => resolve());
      } else {
        resolve();
      }
    } else {
      resolve();
    }
  });
}

// Kick off preload as soon as DOM is ready (uses your original success.mp3)
document.addEventListener("DOMContentLoaded", () => {
  loadDing("/static/success.mp3"); // keep this path to your existing file
});

// ===================== Helpers & UI wiring ===========================
function clamp(val, min, max) {
  const n = Number(val);
  if (Number.isNaN(n)) return min;
  return Math.max(min, Math.min(max, n));
}

function linkNumberAndRange(numId, rangeId, labelId) {
  const num = document.getElementById(numId);
  const rng = document.getElementById(rangeId);
  const label = document.getElementById(labelId);
  if (!num || !rng || !label) return;

  const min = Number(rng.min), max = Number(rng.max);

  const updateFromNum = () => {
    const v = clamp(num.value, min, max);
    num.value = v;
    rng.value = v;
    label.textContent = v;
  };

  const updateFromRange = () => {
    const v = clamp(rng.value, min, max);
    num.value = v;
    label.textContent = v;
  };

  // initialize and wire events
  updateFromNum();
  num.addEventListener("input", updateFromNum);
  rng.addEventListener("input", updateFromRange);
}

async function jsonFetch(url, opts = {}) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.headers.get("content-type")?.includes("application/json")
    ? res.json()
    : res.text();
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

// ======================= Workouts table ==============================
async function fetchWorkouts() {
  try {
    const data = await jsonFetch("/api/workouts");

    // (Optional) newest-first sort in the browser if server isn't sorting:
    // data.sort((a, b) => (new Date(b.date) - new Date(a.date)) || ((b.id??0) - (a.id??0)));

    const tbody = document.querySelector("#workouts-table tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    for (const w of data) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${(w.date || "").slice(0,10)}</td>
        <td>${w.exercise ?? ""}</td>
        <td>${w.sets ?? ""}</td>
        <td>${w.reps ?? ""}</td>
        <td>${w.weight ?? ""}</td>
        <td>${w.notes ?? ""}</td>
        <td>
          <button class="delete-btn" data-id="${w.id}">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    }
    bindDeleteButtons();
    setStatus(`Loaded ${data.length} workout${data.length === 1 ? "" : "s"}.`, "ok");
  } catch (err) {
    setStatus(`Failed to load workouts: ${err.message}`, "err");
  }
}

function bindDeleteButtons() {
  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const id = e.currentTarget.getAttribute("data-id");
      if (!id) return;
      if (!confirm("Delete this workout?")) return;
      try {
        await fetch(`/api/workouts/${id}`, { method: "DELETE" });
        await fetchWorkouts();
      } catch (err) {
        setStatus(`Delete failed: ${err.message}`, "err");
      }
    });
  });
}

function setStatus(msg, kind = "ok") {
  const el = document.getElementById("status");
  if (!el) return;
  el.textContent = msg;
  el.style.color = kind === "err" ? "#ffaaaa" : "#9ecbff";
}

/** Highlight the row that matches the payload we just sent */
function highlightNewlyAddedRow(payload) {
  const tbody = document.querySelector("#workouts-table tbody");
  if (!tbody) return;

  let match = null;
  const rows = tbody.querySelectorAll("tr");
  rows.forEach((tr) => {
    const tds = tr.querySelectorAll("td");
    if (tds.length < 6) return;
    const [d, ex, sets, reps, w, notes] = tds;
    const dateTxt = (d.textContent || "").slice(0,10);
    if (
      dateTxt === (payload.date || "").slice(0,10) &&
      (ex.textContent || "") === (payload.exercise || "") &&
      (sets.textContent || "") == String(payload.sets || "") &&
      (reps.textContent || "") == String(payload.reps || "") &&
      (w.textContent || "") == String(payload.weight || "") &&
      (notes.textContent || "") === (payload.notes || "")
    ) {
      match = tr;
    }
  });

  // Fallback: if we didn't find an exact row, highlight the last row
  if (!match) match = tbody.lastElementChild;

  if (match) {
    match.classList.remove("shine"); // restart animation if applied before
    void match.offsetWidth;          // reflow hack
    match.classList.add("shine");
  }
}

// ========================= Form handling ============================
function wireForm() {
  const form = document.getElementById("log-form");
  if (!form) return;

  // Dual-mode inputs (number <-> range)
  linkNumberAndRange("sets_num", "sets_range", "sets_value");
  linkNumberAndRange("reps_num", "reps_range", "reps_value");
  linkNumberAndRange("weight_num", "weight_range", "weight_value");

  // Default date
  const dateInput = document.getElementById("date");
  if (dateInput && !dateInput.value) dateInput.value = todayISO();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      date: form.date?.value || todayISO(),
      exercise: form.exercise?.value?.trim(),
      sets: parseInt(form.sets?.value || "0", 10),
      reps: parseInt(form.reps?.value || "0", 10),
      weight: parseFloat(form.weight?.value || "0"),
      notes: form.notes?.value?.trim() || ""
    };

    if (!payload.exercise) {
      setStatus("Please enter an exercise name.", "err");
      return;
    }

    try {
      // Save on server
      await jsonFetch("/api/workouts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      // Reset inputs to sensible defaults
      form.exercise.value = "";
      form.sets.value = "3";
      form.reps.value = "8";
      form.weight.value = "135";
      if (dateInput) dateInput.value = todayISO();
      // keep sliders in sync after reset
      linkNumberAndRange("sets_num", "sets_range", "sets_value");
      linkNumberAndRange("reps_num", "reps_range", "reps_value");
      linkNumberAndRange("weight_num", "weight_range", "weight_value");

      // Wait for your original success.mp3 to START, then update UI
      await playDingAsync();

      // Refresh table and highlight the row we just added
      await fetchWorkouts();
      highlightNewlyAddedRow(payload);

      setStatus("Workout added.", "ok");
    } catch (err) {
      setStatus(`Failed to add workout: ${err.message}`, "err");
    }
  });
}

// ============================ Init =================================
document.addEventListener("DOMContentLoaded", () => {
  wireForm();
  fetchWorkouts();
});

  wireForm();
  fetchWorkouts();
});
