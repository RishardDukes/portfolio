function qs(id) {
  return document.getElementById(id);
}

function playSuccessSound() {
  const sfx = new Audio("/static/sounds/success.mp3");
  sfx.volume = 0.9;
  sfx.play().catch((err) => {
    console.warn("Success sound failed:", err);
  });
}

function sparkle(el) {
  if (!el) return;
  el.classList.remove("glistening");
  void el.offsetWidth;
  el.classList.add("glistening");

  const burst = document.createElement("span");
  burst.className = "sparkle";
  el.appendChild(burst);

  setTimeout(() => {
    burst.remove();
    el.classList.remove("glistening");
  }, 900);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatNumber(value) {
  return new Intl.NumberFormat().format(Number(value || 0));
}

function formatWeight(value) {
  const num = Number(value || 0);
  return Number.isInteger(num) ? String(num) : num.toFixed(1);
}

function linkNumberAndRange(numberId, rangeId, valueId) {
  const numberInput = qs(numberId);
  const rangeInput = qs(rangeId);
  const valueLabel = qs(valueId);
  if (!numberInput || !rangeInput) return;

  const syncFromNumber = () => {
    rangeInput.value = numberInput.value || rangeInput.min || 0;
    if (valueLabel) valueLabel.textContent = numberInput.value || "0";
  };

  const syncFromRange = () => {
    numberInput.value = rangeInput.value;
    if (valueLabel) valueLabel.textContent = rangeInput.value;
  };

  syncFromNumber();
  numberInput.addEventListener("input", syncFromNumber);
  rangeInput.addEventListener("input", syncFromRange);
}

function setStatus(message, targetId = "status") {
  const el = qs(targetId);
  if (el) el.textContent = message;
}

function setCoachMessage(message) {
  const coach = qs("coach-status");
  if (coach) coach.textContent = message;
}

function updateSummary(summary) {
  if (qs("stat-total-workouts")) {
    qs("stat-total-workouts").textContent = formatNumber(summary.total_workouts);
  }
  if (qs("stat-unique-exercises")) {
    qs("stat-unique-exercises").textContent = formatNumber(summary.unique_exercises);
  }
  if (qs("stat-total-volume")) {
    qs("stat-total-volume").textContent = formatNumber(summary.total_volume);
  }
  if (qs("stat-recent-pr")) {
    qs("stat-recent-pr").textContent = formatWeight(summary.recent_pr);
  }
}

async function fetchSummary() {
  try {
    const res = await fetch("/api/workouts/summary", {
      headers: { Accept: "application/json" }
    });
    if (!res.ok) throw new Error("summary failed");
    updateSummary(await res.json());
  } catch (err) {
    console.warn("Summary load failed:", err);
  }
}

async function fetchWorkouts() {
  const tbody = qs("workouts-body");
  if (!tbody) return;

  try {
    const res = await fetch("/api/workouts", {
      headers: { Accept: "application/json" }
    });
    if (!res.ok) throw new Error(`Failed to load workouts: ${res.status}`);

    const workouts = await res.json();

    if (!Array.isArray(workouts) || workouts.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8">No workouts logged yet.</td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = workouts.map((w) => `
      <tr data-id="${w.id}">
        <td>${escapeHtml(w.date || "")}</td>
        <td>${escapeHtml(w.exercise || "")}</td>
        <td>${escapeHtml(w.sets ?? "")}</td>
        <td>${escapeHtml(w.reps ?? "")}</td>
        <td>${escapeHtml(formatWeight(w.weight ?? 0))}</td>
        <td>${escapeHtml(formatNumber(w.volume ?? 0))}</td>
        <td>${escapeHtml(w.notes || "—")}</td>
        <td><button type="button" class="delete-btn" data-id="${w.id}">Delete</button></td>
      </tr>
    `).join("");

    tbody.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        if (!id) return;

        try {
          const res = await fetch(`/api/workouts/${id}`, { method: "DELETE" });
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`Delete failed: ${text}`);
          }

          setStatus("Workout deleted.");
          await Promise.all([fetchWorkouts(), fetchSummary()]);
        } catch (err) {
          console.error(err);
          setStatus("Failed to delete workout.");
        }
      });
    });
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `
      <tr>
        <td colspan="8">Failed to load workouts.</td>
      </tr>
    `;
    setStatus("Failed to load workouts.");
  }
}

async function submitWorkout(payload) {
  const res = await fetch("/api/workouts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to add workout: ${text}`);
  }

  playSuccessSound();
  return res.json();
}

function resetFormDefaults() {
  const dateInput = qs("date");
  if (dateInput) dateInput.value = new Date().toISOString().slice(0, 10);

  const defaults = [
    ["sets_num", "sets_range", "sets_value", "3"],
    ["reps_num", "reps_range", "reps_value", "8"],
    ["weight_num", "weight_range", "weight_value", "135"],
  ];

  defaults.forEach(([numId, rangeId, valueId, value]) => {
    const num = qs(numId);
    const range = qs(rangeId);
    const label = qs(valueId);
    if (num) num.value = value;
    if (range) range.value = value;
    if (label) label.textContent = value;
  });
}

function wireForm() {
  const form = qs("log-form");
  if (!form) return;

  linkNumberAndRange("sets_num", "sets_range", "sets_value");
  linkNumberAndRange("reps_num", "reps_range", "reps_value");
  linkNumberAndRange("weight_num", "weight_range", "weight_value");
  resetFormDefaults();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      exercise: qs("exercise")?.value?.trim() || "",
      date: qs("date")?.value || "",
      sets: Number(qs("sets_num")?.value || 0),
      reps: Number(qs("reps_num")?.value || 0),
      weight: Number(qs("weight_num")?.value || 0),
      notes: qs("notes")?.value?.trim() || ""
    };

    if (!payload.exercise) {
      setStatus("Please enter an exercise.");
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    setStatus("Adding workout...");

    try {
      const result = await submitWorkout(payload);
      await Promise.all([fetchWorkouts(), fetchSummary()]);
      form.reset();
      resetFormDefaults();
      setStatus("Workout added.");

      const coachText =
        typeof result.hercules === "string"
          ? result.hercules
          : result.hercules?.message || "Hercules is ready for the next entry.";

      setCoachMessage(coachText);
      sparkle(document.querySelector(".content-card"));
    } catch (err) {
      console.error(err);
      setStatus("Failed to add workout.");
      setCoachMessage("Need a clean set before I can coach the next move.");
      alert(err.message);
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireForm();
  fetchWorkouts();
  fetchSummary();
});