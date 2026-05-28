document.addEventListener('DOMContentLoaded', () => {
  const timers = [
    document.getElementById('nav-timer'),
    document.getElementById('dash-timer'),
    document.getElementById('log-active-duration'),
  ].filter(Boolean);
  if (!timers.length) return;

  const pad = (n) => String(n).padStart(2, '0');

  timers.forEach((timerEl) => {
    const startIso = timerEl.getAttribute('data-start');
    const start = startIso ? new Date(startIso) : null;
    if (!start || Number.isNaN(start.getTime())) return;

    const update = () => {
      const diff = Math.max(0, Date.now() - start.getTime());
      const hours = Math.floor(diff / 3600000);
      const minutes = Math.floor((diff % 3600000) / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      timerEl.textContent = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
    };

    update();
    setInterval(update, 1000);
  });
});
