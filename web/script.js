let score = 0;
let energy = 10;
const coin = document.getElementById("coin");
const scoreDisplay = document.getElementById("score");
const energyFill = document.getElementById("energy-fill");
const energyText = document.getElementById("energy-text");

coin.addEventListener("click", () => {
  if (energy > 0) {
    energy--;
    score += Math.floor(Math.random() * 5) + 1;
    scoreDisplay.textContent = score;
    updateEnergy();
    coin.style.transform = "scale(0.9)";
    setTimeout(() => coin.style.transform = "scale(1)", 100);
  } else {
    alert("⚡ Energiya tugagan! Kuting...");
  }
});

function updateEnergy() {
  energyFill.style.width = `${(energy / 10) * 100}%`;
  energyText.textContent = `⚡ ${energy} / 10`;
}

setInterval(() => {
  if (energy < 10) {
    energy++;
    updateEnergy();
  }
}, 5000);

document.getElementById("boost-btn").onclick = () => {
  energy = 10;
  updateEnergy();
  alert("⚡ Energiya to‘ldi!");
};

document.getElementById("invite-btn").onclick = () => {
  alert("👥 Do‘stlaringizni taklif qiling va bonus oling!");
};
