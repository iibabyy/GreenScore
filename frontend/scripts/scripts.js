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

function getGreenScoreUrlImg(score) {
	if (score < 20)
		return "assets/green_score/e.svg";
	else if (score < 40)
		return "assets/green_score/b.svg";
	else if (score < 60)
		return "assets/green_score/c.svg";
	else if (score < 80)
		return "assets/green_score/b.svg";
	else
		return "assets/green_score/a.svg";
}

function showResult() {
    const modalBody = document.getElementById("test");
    modalBody.classList.add("text-lg"); // Augmente la taille de tout le texte
    
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
		const oneMedicine = document.createElement('div');
		
		// Ajouter une classe spéciale pour le premier médicament
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
		
		// Si c'est le premier médicament, appliquer une bordure ou un fond distinct et ajouter le badge
		if (i === 0) {
			oneMedicine.classList.add("bg-yellow-100", "border-yellow-500", "shadow-lg");
	
			// Ajouter le badge "Best Recommendation" en haut à gauche
			const bestRecommendationBadge = document.createElement('div');
			bestRecommendationBadge.innerText = "Best Recommendation";
			bestRecommendationBadge.classList.add(
				"absolute", 
				"top-0", 
				"left-0", 
				"bg-green-500", 
				"text-white", 
				"px-4", 
				"py-1", 
				"rounded-tl-lg",
				"rounded-br-lg", // Coins arrondis en bas à droite pour le badge
				"text-sm", 
				"font-semibold", 
				"shadow-md"
			);
	
			oneMedicine.classList.add("relative"); // Assure-toi que le conteneur est positionné pour accueillir le badge
			oneMedicine.appendChild(bestRecommendationBadge);
		}
	
		const imageContainer = document.createElement('div');
		imageContainer.classList.add("relative", "w-full", "flex", "justify-center");
	
		const medicineImg = document.createElement('img');
		medicineImg.src = "assets/fortenuit-8h.jpg";
		medicineImg.alt = `${MEDICINE_NAME} image`;
		medicineImg.classList.add("h-40", "w-40", "object-cover", "rounded-full", "border", "border-gray-100", "shadow-sm");
	
		const medicineGreenScoreImg = document.createElement('img');
		medicineGreenScoreImg.src = getGreenScoreUrlImg(GREEN_SCORE);
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
	
		const medicineInfos = document.createElement('div');
		medicineInfos.classList.add(
			"flex", 
			"flex-col", 
			"h-full",
			"justify-between"
		);
	
		const medicineName = document.createElement('h2');
		medicineName.classList.add(
			"text-2xl", 
			"font-semibold", 
			"text-gray-800",
			"mb-4",
			"capitalize"
		);
		medicineName.innerHTML = MEDICINE_NAME;
	
		const ratingContainer = document.createElement('div');
		ratingContainer.classList.add(
			"grid", 
			"grid-cols-2", 
			"gap-3",
			"text-lg",
			"mb-4"
		);
	
		ratingPoints.forEach(point => {
			const ratingPoint = document.createElement('div');
			ratingPoint.classList.add(
				"flex", 
				"items-center", 
				"gap-2",
				"bg-gray-50",
				"p-2",
				"rounded-lg"
			);
			
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
	
		const moreInfoButton = document.createElement('button');
		moreInfoButton.innerHTML = "En savoir plus";
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
			console.log(`Afficher plus d'informations pour ${MEDICINE_NAME}`);
		});
	
		medicineInfos.appendChild(medicineName);
		medicineInfos.appendChild(ratingContainer);
		medicineInfos.appendChild(moreInfoButton);
	
		oneMedicine.appendChild(imageContainer);
		oneMedicine.appendChild(medicineInfos);
	
		gridContainer.appendChild(oneMedicine);
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