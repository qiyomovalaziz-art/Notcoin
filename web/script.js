const tg = window.Telegram.WebApp;
tg.expand();

let user = tg.initDataUnsafe?.user;
let user_id = user?.id;

const coin = document.getElementById("coin");
const coinsText = document.getElementById("coins");
const energyFill = document.getElementById("energy-fill");
const bonusBtn = document.getElementById("bonus");

function updateEnergy(value) {
  energyFill.style.width = (value * 10) + "%";
}

coin.addEventListener("click", () => {
  fetch("/add_coin", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id }),
  })
    .then(res => res.json())
    .then(data => {
      coinsText.textContent = data.coins;
      updateEnergy(data.energy);
      coin.style.transform = "scale(0.9)";
      setTimeout(() => coin.style.transform = "scale(1)", 100);
    })
    .catch(err => console.log(err));
});

bonusBtn.addEventListener("click", () => {
  fetch("/daily_bonus", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id }),
  })
    .then(res => res.json())
    .then(data => {
      if (data.bonus) {
        alert("🎁 Kunlik bonus: +" + data.bonus);
      } else {
        alert("⏳ Bugun bonus olingan!");
      }
    });
});
