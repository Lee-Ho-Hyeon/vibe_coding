const playerDetail = document.getElementById("playerDetail");

const params = new URLSearchParams(window.location.search);
const qid = params.get("qid");

async function loadPlayerDetail() {
    if (!qid) {
        playerDetail.innerHTML = "<p>선수 정보가 없습니다.</p>";
        return;
    }

    const response = await fetch(`http://127.0.0.1:8000/players/${qid}`);
    const player = await response.json();

    playerDetail.innerHTML = `
        <h2>${player.display_name}</h2>
        <p><strong>국적:</strong> ${player.countries.join(", ")}</p>

        <h3>클럽 경력</h3>
        <ul>
            ${player.clubs.map(club => `<li>${club.club_name}</li>`).join("")}
        </ul>
    `;
}

loadPlayerDetail();