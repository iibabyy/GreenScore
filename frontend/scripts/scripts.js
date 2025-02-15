const medications = [
	{ name: "Paracétamol Bio", score: "A", impact: "Très faible impact", image: "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&q=80&w=200&h=200" },
	{ name: "Ibuprofène Eco", score: "B", impact: "Faible impact", image: "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&q=80&w=200&h=200" },
	{ name: "Amoxicilline", score: "C", impact: "Impact modéré", image: "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&q=80&w=200&h=200" }
];

const medicationsContainer = document.getElementById("medications");

medications.forEach(med => {
	const card = document.createElement("div");
	card.className = "bg-white rounded-xl shadow-sm overflow-hidden";
	card.innerHTML = `
		<img src="${med.image}" alt="${med.name}" class="w-full h-48 object-cover" />
		<div class="p-4">
			<div class="flex items-center justify-between mb-2">
				<h3 class="text-lg font-semibold">${med.name}</h3>
				<span class="px-3 py-1 rounded-full text-sm font-medium ${med.score === 'A' ? 'bg-green-100 text-green-800' : med.score === 'B' ? 'bg-yellow-100 text-yellow-800' : 'bg-orange-100 text-orange-800'}">Score ${med.score}</span>
			</div>
			<p class="text-gray-600">${med.impact}</p>
		</div>
	`;
	medicationsContainer.appendChild(card);
});