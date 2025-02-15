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

function showResult() {
	const modalBody = document.getElementById("test");
	const nbResult = 100;
	// TODO: appeler le backend de Idrissa 
	// on recupere le resultat
	modalBody.innerHTML = ""
	
	const nbResultText = document.createElement('p');
	nbResultText.innerHTML = `${nbResult} Results`;
	modalBody.appendChild(nbResultText);
	
	for (let i = 0; i < nbResult; i++) {
		const oneMedicine = document.createElement('div');
		oneMedicine.classList.add("border-2", "border-solid", "border-black", "rounded-sm", "h-24");
		oneMedicine.innerHTML = "ahaha";
		modalBody.appendChild(oneMedicine);
	}

}

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

function sendPrompt() {
	let prompt = document.getElementById("search");

	if (prompt === null || prompt.value === "")
		return;

	
	openModal(prompt.value);
	console.log(`[${prompt.value}]`);
	prompt.value = "";
}

document.getElementById("search").addEventListener('keypress', (event) => {
	if (event.key === "Enter")
		sendPrompt();
});


window.sendPrompt = sendPrompt;
window.closeModalFunc = closeModalFunc;