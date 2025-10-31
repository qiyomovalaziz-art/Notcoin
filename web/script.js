let coins = 0;
let energy = 5500;

const coinCount = document.getElementById("coinCount");
const energyDisplay = document.getElementById("energy");
const energyFill = document.getElementById("energy-fill");
const coin = document.getElementById("coin");

coin.addEventListener("click", () => {
  if (energy > 0) {
    coins++;
    energy--;
    coinCount.textContent = coins.toLocaleString();
    energyDisplay.textContent = energy;
    energyFill.style.width = (energy / 5500) * 100 + "%";
  }
});
