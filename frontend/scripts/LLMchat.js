

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

    if (!message) return;

    chatInput.setAttribute("disabled", "true");
    chatInput.setAttribute("aria-busy", "true");

    // Création du message utilisateur
    const userMessage = document.createElement("div");
    userMessage.classList.add("flex", "justify-end", "items-start", "mb-2");

    // Conteneur du message utilisateur (pour assurer un bon alignement)
    const userContainer = document.createElement("div");
    userContainer.classList.add("flex", "items-start", "space-x-2");

    // Bulle de message
    const userBubble = document.createElement("div");
    userBubble.classList.add(
        "bg-green-500", "text-white", "px-4", "py-2", "rounded-lg",
        "shadow-md", "max-w-xs", "text-sm", "text-wrap"
    );
    userBubble.textContent = message;

    // Avatar utilisateur
    const userAvatar = document.createElement("img");
    userAvatar.src = "assets/user.jpg"; // Remplace avec l'image de l'utilisateur
    userAvatar.alt = "User";
    userAvatar.classList.add("w-8", "h-8", "rounded-full", "ml-2");

    userContainer.appendChild(userBubble);
    userContainer.appendChild(userAvatar);
    userMessage.appendChild(userContainer);
    chatBox.prepend(userMessage);

    // Effacer l'input après l'envoi
    chatInput.value = "";

    // Simuler une réponse du bot après 1 seconde
    setTimeout(() => {
        const botMessage = document.createElement("div");
        botMessage.classList.add("flex", "justify-start", "items-start", "mb-2");

        const botContainer = document.createElement("div");
        botContainer.classList.add("flex", "items-start", "space-x-2");

        const botAvatar = document.createElement("img");
        botAvatar.src = "assets/mistral.webp"; // Remplace avec l'image du bot
        botAvatar.alt = "Bot";
        botAvatar.classList.add("w-8", "h-8", "rounded-full", "mr-2");

        const botBubble = document.createElement("div");
        botBubble.classList.add(
            "bg-gray-200", "text-gray-800", "px-4", "py-2", "rounded-lg",
            "shadow-md", "max-w-xs", "text-sm"
        );
        botBubble.textContent = generateLoremIpsum();

        botContainer.appendChild(botAvatar);
        botContainer.appendChild(botBubble);
        botMessage.appendChild(botContainer);
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

window.closeModal = closeModal;
window.backToFirstModal = backToFirstModal;
window.closeChatModal = closeChatModal;