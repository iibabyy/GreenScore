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
    nbResultText.classList.add("text-lg", "font-medium", "mb-4", "text-gray-700");
    
    const gridContainer = document.createElement('div');
    gridContainer.classList.add("grid", "grid-cols-2", "gap-6", "w-full");

    modalBody.appendChild(nbResultText);
    modalBody.appendChild(gridContainer);

    for (let i = 0; i < nbResult; i++) {
        const oneMedicine = document.createElement('div');
        oneMedicine.classList.add(
            "border", 
            "border-gray-200", 
            "rounded-xl", 
            "h-64", // Hauteur augmentée pour accommoder le bouton
            "flex", 
            "items-center", 
            "p-6",
            "gap-6",
            "bg-white",
            "shadow-sm",
            "hover:shadow-md",
            "transition-shadow",
            "duration-200"
        );

        const imageContainer = document.createElement('div');
        imageContainer.classList.add("relative", "h-full", "flex", "items-center");

        const medicineImg = document.createElement('img');
        medicineImg.src = "assets/fortenuit-8h.jpg";
        medicineImg.alt = `${MEDICINE_NAME} image`;
        medicineImg.classList.add("h-40", "w-40", "object-cover", "rounded-full", "border", "border-gray-100", "shadow-sm");

        const medicineGreenScoreImg = document.createElement('img');
        medicineGreenScoreImg.src = getGreenScoreUrlImg(GREEN_SCORE);
        medicineGreenScoreImg.alt = "Green Score Image";
        medicineGreenScoreImg.classList.add(
            "w-20", 
            "h-20", 
            "absolute", 
            "top-0", 
            "right-0", 
            "-translate-y-4", 
            "translate-x-4",
            "shadow-lg"
        );

        imageContainer.appendChild(medicineImg);
        imageContainer.appendChild(medicineGreenScoreImg);

        const medicineInfos = document.createElement('div');
        medicineInfos.classList.add(
            "flex", 
            "flex-col", 
            "h-full", 
            "flex-grow",
            "py-2"
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
            "text-sm",
            "mb-4" // Ajout d'une marge en bas
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

		// Ajout du bouton "En savoir plus"
		const moreInfoButton = document.createElement('button');
		moreInfoButton.innerHTML = "En savoir plus";
		moreInfoButton.classList.add(
			"mt-auto",
			"bg-green-500",
			"hover:bg-green-600",
			"text-white",
			"font-medium",
			"py-4",  // Encore plus grand en hauteur
			"px-3",
			"rounded-lg",
			"transition-colors",
			"duration-200",
			"text-xs",
			"w-32",  // Plus serré en largeur
			"ml-auto" // Le pousse vers la droite
		);



        // Ajout de l'événement click
        moreInfoButton.addEventListener('click', () => {
            // Ici vous pouvez ajouter la logique pour afficher plus d'informations
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