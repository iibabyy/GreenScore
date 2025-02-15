

function sendPrompt() {
	let prompt = document.getElementById("search");

	if (prompt === null)
		return;

	console.log(prompt.value);
	prompt.value = "";
}

document.getElementById("search").addEventListener('keypress', (event) => {
	if (event.key === "Enter")
		sendPrompt();
});

window.sendPrompt = sendPrompt;