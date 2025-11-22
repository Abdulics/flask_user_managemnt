document.addEventListener('DOMContentLoaded', () => {
  const timerEl = document.getElementById('nav-timer');
  if (!timerEl) return;
  const startIso = timerEl.getAttribute('data-start');
  if (!startIso) return;
  const start = new Date(startIso);

  const update = () => {
    const diff = Date.now() - start.getTime();
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    const pad = (n) => String(n).padStart(2, '0');
    timerEl.textContent = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  };

  update();
  setInterval(update, 1000);
});

document.addEventListener('DOMContentLoaded', () => {
  const dashTimerEl = document.getElementById('dash-timer');
  if (!dashTimerEl) return;
  const startIso = dashTimerEl.getAttribute('data-start');
  if (!startIso) return;
  const start = new Date(startIso);
  const update = () => {
    const diff = Date.now() - start.getTime();
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    const pad = (n) => String(n).padStart(2, '0');
    dashTimerEl.textContent = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  };
  update();
  setInterval(update, 1000);
});
