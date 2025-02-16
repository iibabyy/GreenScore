// Fonction pour fermer la modal
function closeModal() {
    const modal = document.getElementById("modal");
    const modalContent = modal.querySelector("div");

    modalContent.classList.remove("scale-100", "opacity-100");
    modalContent.classList.add("scale-95", "opacity-0");
    setTimeout(() => {
        modal.classList.remove("flex");
        modal.classList.add("hidden");
    }, 300);
}

// Fonction pour ouvrir la modal avec un message
function openModal(message) {
    const modal = document.getElementById("modal");
    const modalContent = modal.querySelector("div");
    const userPrompt = document.getElementById("user-prompt");

    modal.classList.remove("hidden");
    setTimeout(() => {
        modal.classList.add("flex");
        modalContent.classList.remove("scale-95", "opacity-0");
        modalContent.classList.add("scale-100", "opacity-100");
    }, 10);
    userPrompt.innerText = message;
	showResult();
}

// Fonction pour afficher les résultats dans la modal
function showResult() {
    const modalBody = document.getElementById("test");
    modalBody.classList.add("text-lg");

    const nbResult = 4;
    const MEDICINE_NAME = "fortenuit 8h";
    const GREEN_SCORE = 40;

    const ratingPoints = [
        { label: "Efficacité", score: 4 },
        { label: "Effets secondaires", score: 3 },
        { label: "Prix", score: 5 },
        { label: "Facilité d'utilisation", score: 4 }
    ];

    modalBody.innerHTML = "";

    const nbResultText = document.createElement('p');
    nbResultText.innerHTML = `${nbResult} Results`;
    nbResultText.classList.add("text-xl", "font-medium", "mb-4", "text-gray-700");

    const gridContainer = document.createElement('div');
    gridContainer.classList.add("grid", "grid-cols-1", "lg:grid-cols-2", "gap-6", "w-full");

    modalBody.appendChild(nbResultText);
    modalBody.appendChild(gridContainer);

    for (let i = 0; i < nbResult; i++) {
        const oneMedicine = createMedicineCard(MEDICINE_NAME, GREEN_SCORE, ratingPoints, i === 0);
        gridContainer.appendChild(oneMedicine);
    }
}

// Fonction pour créer une carte de médicament
function createMedicineCard(name, greenScore, ratingPoints, isBestRecommendation) {
    const oneMedicine = document.createElement('div');
    oneMedicine.classList.add(
        "border",
        "border-gray-200",
        "rounded-xl",
        "h-auto",
        "flex",
        "flex-col",
        "p-6",
        "gap-6",
        "bg-white",
        "shadow-sm",
        "hover:shadow-md",
        "transition-shadow",
        "duration-200"
    );

    if (isBestRecommendation) {
        oneMedicine.classList.add("bg-yellow-100", "border-yellow-500", "shadow-lg");
        const bestRecommendationBadge = createBestRecommendationBadge();
        oneMedicine.classList.add("relative");
        oneMedicine.appendChild(bestRecommendationBadge);
    }

    const imageContainer = createImageContainer(name, greenScore);
    const medicineInfos = createMedicineInfos(name, ratingPoints);

    oneMedicine.appendChild(imageContainer);
    oneMedicine.appendChild(medicineInfos);

    return oneMedicine;
}

// Fonction pour créer le badge "Best Recommendation"
function createBestRecommendationBadge() {
    const badge = document.createElement('div');
    badge.innerText = "Best Recommendation";
    badge.classList.add(
        "absolute",
        "top-0",
        "left-0",
        "bg-green-500",
        "text-white",
        "px-4",
        "py-1",
        "rounded-tl-lg",
        "rounded-br-lg",
        "text-sm",
        "font-semibold",
        "shadow-md"
    );
    return badge;
}

// Fonction pour créer le conteneur d'image
function createImageContainer(name, greenScore) {
    const imageContainer = document.createElement('div');
    imageContainer.classList.add("relative", "w-full", "flex", "justify-center");

    const medicineImg = document.createElement('img');
    medicineImg.src = "assets/fortenuit-8h.jpg";
    medicineImg.alt = `${name} image`;
    medicineImg.classList.add("h-40", "w-40", "object-cover", "rounded-full", "border", "border-gray-100", "shadow-sm");

    const medicineGreenScoreImg = document.createElement('img');
    medicineGreenScoreImg.src = getGreenScoreUrlImg(greenScore);
    medicineGreenScoreImg.alt = "Green Score Image";
    medicineGreenScoreImg.classList.add(
        "absolute",
        "bottom-0",
        "right-0",
        "w-16",
        "h-16",
        "sm:w-20",
        "sm:h-20",
        "md:w-24",
        "md:h-24",
        "lg:w-28",
        "lg:h-28"
    );

    imageContainer.appendChild(medicineImg);
    imageContainer.appendChild(medicineGreenScoreImg);

    return imageContainer;
}

// Fonction pour créer les informations du médicament
function createMedicineInfos(name, ratingPoints) {
    const medicineInfos = document.createElement('div');
    medicineInfos.classList.add("flex", "flex-col", "h-full", "justify-between");

    const medicineName = document.createElement('h2');
    medicineName.classList.add("text-2xl", "font-semibold", "text-gray-800", "mb-4", "capitalize");
    medicineName.innerHTML = name;

    const ratingContainer = createRatingContainer(ratingPoints);
    const moreInfoButton = createMoreInfoButton(name);

    medicineInfos.appendChild(medicineName);
    medicineInfos.appendChild(ratingContainer);
    medicineInfos.appendChild(moreInfoButton);

    return medicineInfos;
}

// Fonction pour créer le conteneur de notation
function createRatingContainer(ratingPoints) {
    const ratingContainer = document.createElement('div');
    ratingContainer.classList.add("grid", "grid-cols-2", "gap-3", "text-lg", "mb-4");

    ratingPoints.forEach(point => {
        const ratingPoint = document.createElement('div');
        ratingPoint.classList.add("flex", "items-center", "gap-2", "bg-gray-50", "p-2", "rounded-lg");

        const label = document.createElement('span');
        label.innerHTML = point.label;
        label.classList.add("font-medium", "text-gray-600");

        const score = document.createElement('span');
        score.innerHTML = "⭐".repeat(point.score);
        score.classList.add("text-yellow-400", "ml-auto");

        ratingPoint.appendChild(label);
        ratingPoint.appendChild(score);
        ratingContainer.appendChild(ratingPoint);
    });

    return ratingContainer;
}

// Fonction pour créer le bouton "En savoir plus"
function createMoreInfoButton(name) {
    const moreInfoButton = document.createElement('button');
    moreInfoButton.innerHTML = "Show more";
    moreInfoButton.classList.add(
        "bg-green-500",
        "hover:bg-green-600",
        "text-white",
        "font-medium",
        "py-3",
        "px-6",
        "rounded-lg",
        "transition-colors",
        "duration-200",
        "text-lg",
        "w-full",
        "lg:w-auto",
        "self-end"
    );

    moreInfoButton.addEventListener('click', () => {
		openChatModal();
        console.log(`Afficher plus d'informations pour ${name}`); // TODO: a retirer
    });

    return moreInfoButton;
}

// Fonction pour obtenir l'URL de l'image du Green Score
function getGreenScoreUrlImg(score) {
    if (score < 20) return "assets/green_score/e.svg";
    else if (score < 40) return "assets/green_score/b.svg";
    else if (score < 60) return "assets/green_score/c.svg";
    else if (score < 80) return "assets/green_score/b.svg";
    else return "assets/green_score/a.svg";
}

// Fonction pour ouvrir la modal avec le contenu de la page "About"
async function AboutModal(message) {
    const about = document.getElementById("test");
    openModal(message);
    about.innerHTML = await fetch("../pages/About.html").then((response) => response.text());
}

// Fonction pour ouvrir la modal avec le contenu de la page "Info"
async function InfoModal(message) {
    const about = document.getElementById("test");
    openModal(message);
    about.innerHTML = await fetch("../pages/info.html").then((response) => response.text());
}

// Fonction pour envoyer la requête de recherche
function sendPrompt() {
    const prompt = document.getElementById("search");
    if (prompt === null || prompt.value === "") return;

    openModal(prompt.value);
	// TODO: send la recherche a idrissa 
    console.log(`[${prompt.value}]`);
    prompt.value = "";
}

function closeChatModal() {
    const chatModal = document.getElementById("chat-modal");
    const modalContent = chatModal.querySelector("div");


    modalContent.classList.remove("scale-100", "opacity-100");
    modalContent.classList.add("scale-95", "opacity-0");
    setTimeout(() => {
        chatModal.classList.remove("flex");
        chatModal.classList.add("hidden");
    }, 300);
}

function openChatModal() {
    const chatModal = document.getElementById("chat-modal");
	const modalContent = chatModal.querySelector("div");
    chatModal.classList.remove("hidden");
    setTimeout(() => {
		chatModal.classList.add("flex");
        modalContent.classList.remove("scale-95", "opacity-0");
        modalContent.classList.add("scale-100", "opacity-100");
    }, 10);
}

function generateLoremIpsum(wordCount = 50) {
    const loremWords = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
        "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
        "magna", "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis", "nostrud",
        "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea",
        "commodo", "consequat", "duis", "aute", "irure", "dolor", "in", "reprehenderit",
        "in", "voluptate", "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla",
        "pariatur"
    ];

    let loremText = [];
    for (let i = 0; i < wordCount; i++) {
        loremText.push(loremWords[Math.floor(Math.random() * loremWords.length)]);
    }

    return loremText.join(" ") + ".";
}

function sendChatMessage() {
    const chatInput = document.getElementById("chat-llm-input");
    const chatBox = document.getElementById("chat-with-llm");
    const message = chatInput.value.trim();

    if (!message)
		return;

    chatInput.setAttribute("disabled", "true");
    chatInput.setAttribute("aria-busy", "true");

    // Message utilisateur stylisé
    const userMessage = document.createElement("div");
    userMessage.classList.add("flex", "justify-end", "mb-2");

    const messageBubble = document.createElement("div");
    messageBubble.classList.add(
        "bg-green-500", "text-white", "px-4", "py-2", "rounded-lg",
        "shadow-md", "max-w-xs", "text-sm"
    );
    messageBubble.textContent = message;

    userMessage.appendChild(messageBubble);
    chatBox.prepend(userMessage);

    // Effacer l'input après l'envoi
    chatInput.value = "";

    // Simuler une réponse du bot après 1 seconde
    setTimeout(() => {
        const botMessage = document.createElement("div");
        botMessage.classList.add("flex", "justify-start", "mb-2");

        const botBubble = document.createElement("div");
        botBubble.classList.add(
            "bg-gray-200", "text-gray-800", "px-4", "py-2", "rounded-lg",
            "shadow-md", "max-w-xs", "text-sm"
        );
        botBubble.textContent = generateLoremIpsum();

        botMessage.appendChild(botBubble);
        chatBox.prepend(botMessage);

        // Réactiver le champ input après la réponse du bot
        chatInput.removeAttribute("disabled");
        chatInput.removeAttribute("aria-busy");
    }, 1000);
}


function backToFirstModal() {
	closeChatModal();
	// setTimeout(() => {
	// 	openModal();
	// }, 350);
}

// Écouteurs d'événements
document.getElementById("modal").addEventListener("click", function (e) {
    if (e.target === this) {
        closeModal();
    }
});

document.getElementById("chat-llm-input").addEventListener('keypress', (event) => {
    if (event.key === "Enter") sendChatMessage();
});

document.getElementById("search").addEventListener('keypress', (event) => {
    if (event.key === "Enter") sendPrompt();
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

window.sendPrompt = sendPrompt;
window.closeModal = closeModal;
window.backToFirstModal = backToFirstModal;
window.closeChatModal = closeChatModal;