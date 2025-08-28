// === Helpers ===
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

// === Workouts table ===
async function fetchWorkouts() {
  try {
    const data = await jsonFetch("/api/workouts");
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

// === Form handling ===
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
      await jsonFetch("/api/workouts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      // reset sensible defaults
      form.exercise.value = "";
      form.sets.value = "3";
      form.reps.value = "8";
      form.weight.value = "135";
      if (dateInput) dateInput.value = todayISO();
      // keep sliders in sync after reset
      linkNumberAndRange("sets_num", "sets_range", "sets_value");
      linkNumberAndRange("reps_num", "reps_range", "reps_value");
      linkNumberAndRange("weight_num", "weight_range", "weight_value");

      await fetchWorkouts();
      setStatus("Workout added.", "ok");

      // 🔊 Play success sound
      const snd = document.getElementById("success-sound");
      if (snd) {
        snd.currentTime = 0;
        snd.play().catch(() => {}); // ignore autoplay errors
      }
    } catch (err) {
      setStatus(`Failed to add workout: ${err.message}`, "err");
    }
  });
}

// === Init ===
document.addEventListener("DOMContentLoaded", () => {
  wireForm();
  fetchWorkouts();
});
