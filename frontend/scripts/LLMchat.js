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

function openChatModal(product) {
    const chatModal = document.getElementById("chat-modal");
	const modalContent = chatModal.querySelector("div");
    chatModal.classList.remove("hidden");

    setTimeout(() => {
		chatModal.classList.add("flex");
        modalContent.classList.remove("scale-95", "opacity-0");
        modalContent.classList.add("scale-100", "opacity-100");
    }, 10);

	document.getElementById("chat-llm-input").addEventListener('keypress', async (event) => {
		if (event.key === "Enter")
			await sendChatMessage(product);
	});

	document.getElementById("send-llm-message").addEventListener('click', async () => {
		await sendChatMessage(product);
	});
}

function createBotDiv(botResponse) {
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
	botBubble.textContent = botResponse;

	botContainer.appendChild(botAvatar);
	botContainer.appendChild(botBubble);
	botMessage.appendChild(botContainer);

	// Réactiver le champ input après la réponse du bot
	chatInput.removeAttribute("disabled");
	chatInput.removeAttribute("aria-busy");
	return botMessage;
}

function createUserDiv(userPrompt) {
	const userMessage = document.createElement("div");
	userMessage.classList.add("flex", "justify-end", "items-start", "mb-2");

	const userContainer = document.createElement("div");
	userContainer.classList.add("flex", "items-start", "space-x-2");

	const userBubble = document.createElement("div");
	userBubble.classList.add(
		"bg-green-500", "text-white", "px-4", "py-2", "rounded-lg",
		"shadow-md", "max-w-xs", "text-sm", "text-wrap"
	);
	userBubble.textContent = userPrompt;

	const userAvatar = document.createElement("img");
	userAvatar.src = "assets/user.jpg";
	userAvatar.alt = "User";
	userAvatar.classList.add("w-8", "h-8", "rounded-full", "ml-2");

	userContainer.appendChild(userBubble);
	userContainer.appendChild(userAvatar);
	userMessage.appendChild(userContainer);

	return userMessage;
}

async function sendChatMessage(product) {
    const chatInput = document.getElementById("chat-llm-input");
    const chatBox = document.getElementById("chat-with-llm");
    const message = chatInput.value.trim();

    if (!message) return;

    chatInput.setAttribute("disabled", "true");
    chatInput.setAttribute("aria-busy", "true");
   
    chatBox.prepend(createUserDiv(message));

    chatInput.value = "";

	try {
		const headers = new Headers();

		const response = await fetch("http://localhost:8000/ia/discussion",  {
			method: "POST",
			headers: headers,
			body: JSON.stringify({
				'prompt': message,
				'product_id': product.id
			})
		});
		if (!response.ok) {
			console.error("failed to check user creation")
			return;
		}
		const result = await response.json();
		chatBox.prepend(createBotDiv(result.response));

	} catch (error) {
		console.error('Erreur :', error);
	}
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
