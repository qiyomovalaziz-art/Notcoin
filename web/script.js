const tg = window.Telegram?.WebApp;
if (tg) tg.expand();

let balance = 0;
let energy = 100;

const balanceEl = document.getElementById("balance");
const energyEl = document.getElementById("energy");
const energyText = document.getElementById("energy-text");

function earn() {
  if (energy > 0) {
    balance += 10;
    energy -= 5;
    updateUI();
  } else {
    alert("⚡ Energiyangiz tugadi! Kuting yoki boost bosing.");
  }
}

function invite() {
  alert("🤝 Do‘stlaringizni taklif qiling va bonus oling!");
}

function boost() {
  energy = Math.min(100, energy + 50);
  updateUI();
  alert("⚡ Energiyangiz to‘ldi!");
}

function leaderboard() {
  alert("🏆 Reyting tez orada!");
}

function updateUI() {
  balanceEl.textContent = balance.toLocaleString();
  energyEl.style.width = energy + "%";
  energyText.textContent = energy;
}

// Energiyani asta-sekin tiklash
setInterval(() => {
  if (energy < 100) {
    energy += 1;
    updateUI();
  }
}, 3000);
