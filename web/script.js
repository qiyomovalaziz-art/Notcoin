const tg = window.Telegram.WebApp;
const userId = tg.initDataUnsafe?.user?.id;
const coinsEl = document.getElementById("coins");
const energyEl = document.getElementById("energy");
const btn = document.getElementById("click");

btn.onclick = async () => {
  const res = await fetch("/add_coin", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId })
  });
  const data = await res.json();
  if (res.ok) {
    coinsEl.innerText = `🪙 ${data.coins}`;
    energyEl.innerText = `⚡ ${data.energy}/10`;
  } else {
    alert("Energiya tugagan 😴");
  }
};
