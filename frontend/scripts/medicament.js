// Fonction pour envoyer la requête de recherche
async function sendPrompt() {
    const prompt = document.getElementById("search");
    if (prompt === null || prompt.value === "") return;

    openModal(prompt.value.trim());
	await showResult(prompt.value.trim());
    prompt.value = "";

}

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

// Fonction pour ouvrir la modal avec un search
function openModal(search) {
    const modal = document.getElementById("modal");
    const modalContent = modal.querySelector("div");
    const userPrompt = document.getElementById("user-prompt");

    modal.classList.remove("hidden");
    setTimeout(() => {
        modal.classList.add("flex");
        modalContent.classList.remove("scale-95", "opacity-0");
        modalContent.classList.add("scale-100", "opacity-100");
    }, 10);
    userPrompt.innerText = search;
}

async function getProductsFromDatabase(search) {
	try {
		const headers = new Headers();
		const response = await fetch(`http://localhost:8000/products/search/${search}`, {
			method: "GET",
			headers: headers,
		});

		if (!response.ok) {
			console.error("failed to get my info");
			return null;
		}

		const result = await response.json();
		return result;
	} catch (error) {
		console.error("Error: ", error);
	}
	return null;
}

// Fonction pour afficher les résultats dans la modal
async function showResult(search) {
    const modalBody = document.getElementById("default-modal");
    modalBody.classList.add("text-lg");

	const products = await getProductsFromDatabase(search);
	if (products === null)
		return;

	console.log(products);
    const ratingPoints = [
        { label: "Efficacité", score: 4 },
        { label: "Effets secondaires", score: 3 },
        { label: "Prix", score: 5 },
        { label: "Facilité d'utilisation", score: 4 }
    ];

    modalBody.innerHTML = "";

    const nbResultText = document.createElement('p');
    nbResultText.innerHTML = `${products.length} Results`;
    nbResultText.classList.add("text-xl", "font-medium", "mb-4", "text-gray-700");

    const gridContainer = document.createElement('div');
    gridContainer.classList.add("grid", "grid-cols-1", "lg:grid-cols-2", "gap-6", "w-full");

    modalBody.appendChild(nbResultText);
    modalBody.appendChild(gridContainer);

    for (let i = 0; i < products.length; i++) {
        const oneMedicine = createMedicineCard(products[i].name, products[i].score, ratingPoints, i === 0);
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
        score.innerHTML = "▱".repeat(point.score);
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
		openChatModal(produit);
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

window.sendPrompt = sendPrompt;
