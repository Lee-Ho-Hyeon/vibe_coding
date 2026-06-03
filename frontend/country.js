const countryTitle = document.getElementById("countryTitle");
const countryPlayers = document.getElementById("countryPlayers");

const params = new URLSearchParams(window.location.search);
const country = params.get("country");

async function loadCountryPlayers() {
    if (!country) {
        countryPlayers.innerHTML = "<p>국적 정보가 없습니다.</p>";
        return;
    }

    countryTitle.textContent = `${country} 선수 목록`;

    const response = await fetch(
        `http://127.0.0.1:8000/search/country?q=${encodeURIComponent(country)}`
    );
    const players = await response.json();

    countryPlayers.innerHTML = "";

    if (players.length === 0) {
        countryPlayers.innerHTML = "<p>해당 국적의 선수 정보가 없습니다.</p>";
        return;
    }

    players.forEach(player => {
        const item = document.createElement("div");
        item.className = "result-item";
        item.textContent = player.display_name;

        item.addEventListener("click", () => {
            window.location.href = `player.html?qid=${player.qid}`;
        });

        countryPlayers.appendChild(item);
    });
}

loadCountryPlayers();