


//checks which button has an active state
const tablinks = document.getElementsByClassName("tablinks");
for (let i = 0; i < tablinks.length; i++) {
    if (tablinks[i].dataset.state === "active") {
        tablinks[i].classList.add("active");
    }
}

//checks which button is pressed and reloads to appropriate url
document.querySelectorAll(".tablinks").forEach(btn => {
    btn.addEventListener("click", () => {
        window.location.href = btn.dataset.url;
    });
});