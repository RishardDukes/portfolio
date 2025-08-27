async function fetchWorkouts() {
  const res = await fetch('/api/workouts');
  const data = await res.json();
  const tbody = document.querySelector('#workouts-table tbody');
  tbody.innerHTML = '';
  for (const w of data) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${w.date?.slice(0,10) || ''}</td>
      <td>${w.exercise}</td>
      <td>${w.sets ?? ''}</td>
      <td>${w.reps ?? ''}</td>
      <td>${w.weight ?? ''}</td>
      <td>${w.notes ?? ''}</td>
      <td><button data-id="${w.id}" class="delete-btn">Delete</button></td>
    `;
    tbody.appendChild(tr);
  }
  bindDeleteButtons();
}

function bindDeleteButtons() {
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.target.getAttribute('data-id');
      if (!confirm('Delete this workout?')) return;
      const res = await fetch(`/api/workouts/${id}`, { method: 'DELETE' });
      if (res.status === 204) fetchWorkouts();
      else alert('Failed to delete');
    });
  });
}

document.getElementById('log-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const payload = {
    date: form.date.value,
    exercise: form.exercise.value,
    sets: parseInt(form.sets.value || '0', 10),
    reps: parseInt(form.reps.value || '0', 10),
    weight: parseFloat(form.weight.value || '0'),
    notes: form.notes.value
  };
  const res = await fetch('/api/workouts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    form.reset();
    form.date.value = new Date().toISOString().slice(0,10);
    form.sets.value = 3;
    form.reps.value = 8;
    form.weight.value = 135;
    fetchWorkouts();
  } else {
    document.getElementById('status').textContent = 'Failed to add workout';
  }
});

// initial load
fetchWorkouts();
