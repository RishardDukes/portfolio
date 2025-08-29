// main.js - Handles Add button sound + sparkle effect
const addBtn = document.getElementById('add-btn');
const audioEl = document.getElementById('confirm-audio');

async function playConfirmSoundToEnd() {
  return new Promise(async (resolve, reject) => {
    try {
      if (audioEl.readyState < 2) {
        audioEl.load();
      }
      audioEl.currentTime = 0;
      const onEnded = () => {
        audioEl.removeEventListener('ended', onEnded);
        resolve();
      };
      audioEl.addEventListener('ended', onEnded, { once: true });
      const playPromise = audioEl.play();
      if (playPromise && typeof playPromise.then === 'function') {
        await playPromise;
      }
    } catch (err) {
      reject(err);
    }
  });
}

function escapeHtml(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function renderNewWorkoutWithSparkle(workout) {
  const list = document.getElementById('workout-list');
  const li = document.createElement('li');
  li.className = 'sparkle-wrap glistening';
  li.innerHTML = `
    <div class="workout-card">
      <strong>${escapeHtml(workout.name)}</strong>
      <div>${workout.sets} × ${workout.reps}</div>
    </div>
  `;
  const sparkle = document.createElement('div');
  sparkle.className = 'sparkle';
  li.appendChild(sparkle);
  list?.prepend(li);
  setTimeout(() => li.classList.remove('glistening'), 900);
}

async function createWorkout(payload) {
  const res = await fetch('/api/workouts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    credentials: 'include'
  });
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(`Create failed: ${res.status} ${msg}`);
  }
  return res.json();
}

function getWorkoutFormData() {
  const name = (document.getElementById('workout-name')?.value ?? '').trim();
  const reps = Number(document.getElementById('workout-reps')?.value ?? 0);
  const sets = Number(document.getElementById('workout-sets')?.value ?? 0);
  return { name, reps, sets };
}

addBtn?.addEventListener('click', async () => {
  try {
    await playConfirmSoundToEnd();
    const payload = getWorkoutFormData();
    if (!payload.name) {
      alert('Please enter a workout name.');
      return;
    }
    const created = await createWorkout(payload);
    renderNewWorkoutWithSparkle(created);
    document.getElementById('workout-name')?.value = '';
    document.getElementById('workout-reps')?.value = '';
    document.getElementById('workout-sets')?.value = '';
  } catch (err) {
    console.error('Error adding workout:', err);
  }
});
