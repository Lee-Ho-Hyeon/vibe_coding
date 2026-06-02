const searchButton = document.getElementById("searchButton");
const searchResults = document.getElementById("searchResults");
const searchInput = document.getElementById("searchInput");
const loadClubsButton = document.getElementById("loadClubsButton");
const clubList = document.getElementById("clubList");

let typingTimer;

searchInput.addEventListener("input", () => {
    clearTimeout(typingTimer);

    const keyword = searchInput.value.trim();

    if (keyword.length === 0) {
        searchResults.innerHTML = "";
        return;
    }

    typingTimer = setTimeout(() => {
        searchButton.click();
    }, 300);
});

searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        searchButton.click();
    }
});

searchButton.addEventListener("click", async () => {
    const searchType = document.getElementById("searchType").value;
    const keyword = document.getElementById("searchInput").value.trim();

    if (!keyword) {
        searchResults.innerHTML = "";
        searchResults.style.display = "none";
    return;
    }

    let url = "";

    if (searchType === "player") {
        url = `http://127.0.0.1:8000/search/player?q=${encodeURIComponent(keyword)}`;
    } else if (searchType === "country") {
        url = `http://127.0.0.1:8000/search/country-list?q=${encodeURIComponent(keyword)}`;
    } else if (searchType === "club") {
        url = `http://127.0.0.1:8000/search/club?q=${encodeURIComponent(keyword)}`;
    }  

    const response = await fetch(url);
    const data = await response.json();

    searchResults.style.display = "block";

    if (searchType === "country") {
    data.forEach(countryItem => {
        const item = document.createElement("div");
        item.className = "result-item";
        item.textContent = countryItem.country;

        item.addEventListener("click", () => {
            window.location.href =
                `country.html?country=${encodeURIComponent(countryItem.country)}`;
        });

        searchResults.appendChild(item);
    });

    return;
    }

    if (searchType === "club") {
    searchResults.innerHTML = "";

    data.forEach(club => {
        const item = document.createElement("div");
        item.className = "result-item";
        item.textContent = club.club_name;

        item.addEventListener("click", () => {
            window.location.href =
                `club.html?club_qid=${club.club_qid}&club_name=${encodeURIComponent(club.club_name)}`;
        });

        searchResults.appendChild(item);
    });

    return;
    }

    searchResults.innerHTML = "";

    if (data.length === 0) {
        searchResults.innerHTML = "<p>검색 결과가 없습니다.</p>";
        return;
    }

    data.forEach(player => {
        const item = document.createElement("div");
        item.className = "result-item";
        item.textContent = player.display_name;

        item.addEventListener("click", () => {
            window.location.href = `player.html?qid=${player.qid}`;
        });

        searchResults.appendChild(item);
    });

});

loadClubsButton.addEventListener("click", () => {
    window.location.href = "club-list.html";
});