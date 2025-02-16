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


async function InfoModal(message) {
	document.getElementById("test").innerHTML = "";
	const about = document.getElementById("test");
	//add div form About.html to the about modal
	
	const modal = document.getElementById("modal");
	const modalContent = modal.querySelector("div");
	const userPrompt = document.getElementById("user-prompt");
	
	modal.classList.remove("hidden");
	setTimeout(() => {
		modal.classList.add("flex");
		modalContent.classList.remove("scale-100", "opacity-0");
		modalContent.classList.add("scale-100", "opacity-100");
	}, 10);
	about.innerHTML = await fetch("scripts/donuts/donuts.html").then((response) => response.text());
	userPrompt.innerText = message;
}



async function AboutModal(message) {
	document.getElementById("test").innerHTML = "";
	const about = document.getElementById("test");
	//add div form About.html to the about modal
	
	const modal = document.getElementById("modal");
	const modalContent = modal.querySelector("div");
	const userPrompt = document.getElementById("user-prompt");
	
	modal.classList.remove("hidden");
	setTimeout(() => {
		modal.classList.add("flex");
		modalContent.classList.remove("scale-100", "opacity-0");
		modalContent.classList.add("scale-100", "opacity-100");
	}, 10);
	about.innerHTML = await fetch("../About.html").then((response) => response.text());
	userPrompt.innerText = message;
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

document.getElementById("About").addEventListener('click', async() => {
	AboutModal("About page");
});

document.getElementById("learn-more").addEventListener('click', async() => {
	AboutModal("Learn more");
});

document.getElementById("How-it-works").addEventListener('click', async() => {
	InfoModal("Learn more");
});
window.sendPrompt = sendPrompt;
window.closeModalFunc = closeModalFunc;