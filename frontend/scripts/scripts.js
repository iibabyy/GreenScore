function closeModalFunc() {
    const modal = document.getElementById("modal");
    const modalContent = modal.querySelector("div");

	modalContent.classList.remove("scale-100", "opacity-100");
	modalContent.classList.add("scale-95", "opacity-0");
	setTimeout(() => {
		modal.classList.remove("flex");
		modal.classList.add("hidden");
	}, 300);
}

document.getElementById("modal").addEventListener("click", function (e) {
	if (e.target === modal) {
		closeModalFunc();
	}
});


function openModal(message) {
	const modal = document.getElementById("modal");
    const modalContent = modal.querySelector("div");
	const userPrompt = document.getElementById("user-prompt");

	modal.classList.remove("hidden");
	setTimeout(() => {
		modal.classList.add("flex");
		modalContent.classList.remove("scale-95", "opacity-0");
		modalContent.classList.add("scale-100", "opacity-100");
		userPrompt.innerText = message;
	}, 10);
}

function sendPrompt() {
	let prompt = document.getElementById("search");

	if (prompt === null)
		return;

	openModal(prompt.value);
	console.log(prompt.value);
	prompt.value = "";
}

document.getElementById("search").addEventListener('keypress', (event) => {
	if (event.key === "Enter")
		sendPrompt();
});


window.sendPrompt = sendPrompt;
window.closeModalFunc = closeModalFunc;