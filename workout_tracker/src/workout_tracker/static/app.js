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

async function fetchWorkouts() {
  const tbody = document.querySelector("#workouts-table tbody");
  const status = qs("status");

  if (!tbody) return;

  try {
    const res = await fetch("/api/workouts", {
      headers: { "Accept": "application/json" }
    });

    if (!res.ok) {
      throw new Error(`Failed to load workouts: ${res.status}`);
    }

    const workouts = await res.json();

    if (!Array.isArray(workouts) || workouts.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7">No workouts logged yet.</td>
        </tr>
      `;
      if (status) status.textContent = "";
      return;
    }

    tbody.innerHTML = workouts.map((w) => `
      <tr data-id="${w.id}">
        <td>${escapeHtml(w.date || "")}</td>
        <td>${escapeHtml(w.exercise || "")}</td>
        <td>${escapeHtml(w.sets ?? "")}</td>
        <td>${escapeHtml(w.reps ?? "")}</td>
        <td>${escapeHtml(w.weight ?? "")}</td>
        <td>${escapeHtml(w.notes || "")}</td>
        <td>
          <button type="button" class="delete-btn" data-id="${w.id}">Delete</button>
        </td>
      </tr>
    `).join("");

    tbody.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        if (!id) return;

        try {
          const res = await fetch(`/api/workouts/${id}`, {
            method: "DELETE"
          });

          if (!res.ok) {
            const text = await res.text();
            throw new Error(`Delete failed: ${text}`);
          }

          await fetchWorkouts();
        } catch (err) {
          console.error(err);
          alert("Failed to delete workout.");
        }
      });
    });

    if (status) status.textContent = "";
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `
      <tr>
        <td colspan="7">Failed to load workouts.</td>
      </tr>
    `;
    if (status) status.textContent = "Failed to load workouts.";
  }
}

async function submitWorkout(payload) {
  const res = await fetch("/api/workouts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to add workout: ${text}`);
  }

  playSuccessSound();
  return res.json();
}

function wireForm() {
  const form = qs("log-form");
  if (!form) return;

  linkNumberAndRange("sets_num", "sets_range", "sets_value");
  linkNumberAndRange("reps_num", "reps_range", "reps_value");
  linkNumberAndRange("weight_num", "weight_range", "weight_value");

  const dateInput = qs("date");
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0, 10);
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const exercise = qs("exercise")?.value?.trim() || "";
    const date = qs("date")?.value || "";
    const sets = Number(qs("sets_num")?.value || 0);
    const reps = Number(qs("reps_num")?.value || 0);
    const weight = Number(qs("weight_num")?.value || 0);
    const notes = qs("notes")?.value?.trim() || "";

    if (!exercise) {
      alert("Please enter an exercise.");
      return;
    }

    const payload = {
      exercise,
      date,
      sets,
      reps,
      weight,
      notes
    };

    const submitBtn = form.querySelector('button[type="submit"]');
    const status = qs("status");

    if (submitBtn) submitBtn.disabled = true;
    if (status) status.textContent = "Adding workout...";

    try {
      await submitWorkout(payload);
      await fetchWorkouts();

      form.reset();

      if (dateInput) {
        dateInput.value = new Date().toISOString().slice(0, 10);
      }

      qs("sets_num").value = "3";
      qs("sets_range").value = "3";
      qs("sets_value").textContent = "3";

      qs("reps_num").value = "8";
      qs("reps_range").value = "8";
      qs("reps_value").textContent = "8";

      qs("weight_num").value = "135";
      qs("weight_range").value = "135";
      qs("weight_value").textContent = "135";

      if (status) status.textContent = "Workout added.";
      sparkle(document.querySelector(".content-card"));
    } catch (err) {
      console.error(err);
      if (status) status.textContent = "Failed to add workout.";
      alert(err.message);
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireForm();
  fetchWorkouts();
});