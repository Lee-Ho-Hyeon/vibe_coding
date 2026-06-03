const clubTitle = document.getElementById("clubTitle");
const clubPlayers = document.getElementById("clubPlayers");

const params = new URLSearchParams(window.location.search);
const clubQid = params.get("club_qid");
const clubName = params.get("club_name");

async function loadClubPlayers() {
    if (!clubQid) {
        clubPlayers.innerHTML = "<p>클럽 정보가 없습니다.</p>";
        return;
    }

    if (clubName) {
        clubTitle.textContent = decodeURIComponent(clubName);
    }

    const response = await fetch(`http://127.0.0.1:8000/club/${clubQid}`);
    const players = await response.json();

    clubPlayers.innerHTML = "";

    if (players.length === 0) {
        clubPlayers.innerHTML = "<p>해당 클럽의 선수 정보가 없습니다.</p>";
        return;
    }

    players.forEach(player => {
        const item = document.createElement("div");
        item.className = "result-item";
        item.textContent = player.display_name;

        item.addEventListener("click", () => {
            window.location.href = `player.html?qid=${player.qid}`;
        });

        clubPlayers.appendChild(item);
    });
}

loadClubPlayers();