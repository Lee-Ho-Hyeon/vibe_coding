const clubListPage = document.getElementById("clubListPage");

async function loadClubList() {
    const response = await fetch("http://127.0.0.1:8000/clubs");
    const clubs = await response.json();

    clubListPage.innerHTML = "";

    clubs.forEach(club => {
        const item = document.createElement("div");
        item.className = "result-item";
        item.textContent = club.club_name;

        item.addEventListener("click", () => {
            window.location.href =
                `club.html?club_qid=${club.club_qid}&club_name=${encodeURIComponent(club.club_name)}`;
        });

        clubListPage.appendChild(item);
    });
}

loadClubList();