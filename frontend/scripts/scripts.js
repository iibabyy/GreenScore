// Fonction pour ouvrir la modal avec le contenu de la page "About"
async function AboutModal(message) {
    const about = document.getElementById("default-modal");
    openModal(message);
    about.innerHTML = await fetch("../pages/About.html").then((response) => response.text());
}

// Fonction pour ouvrir la modal avec le contenu de la page "Info"
async function InfoModal(message) {
    const about = document.getElementById("default-modal");
    openModal(message);
    about.innerHTML = await fetch("../pages/info.html").then((response) => response.text());
}

// Écouteurs d'événements
document.getElementById("modal").addEventListener("click", function (e) {
    if (e.target === this) {
        closeModal();
    }
});



document.getElementById("search").addEventListener('keypress', async (event) => {
    if (event.key === "Enter") 
		await sendPrompt();
});

document.getElementById("About").addEventListener('click', () => {
    AboutModal("About page");
});

document.getElementById("learn-more").addEventListener('click', () => {
    AboutModal("Learn more");
});

document.getElementById("How-it-works").addEventListener('click', () => {
    InfoModal("Learn more");
});
