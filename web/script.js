let coins = 0;
const coinsEl = document.getElementById("coins");

document.querySelector(".coin").addEventListener("click", () => {
    coins += 1;
    coinsEl.textContent = coins.toLocaleString();
});
