const AboutPage = () => {
  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">À Propos de GreenScore</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4">Notre Mission</h2>
        <p className="text-gray-700 mb-4">
          GreenScore a pour mission de vous aider à faire des choix éclairés concernant les compléments alimentaires en tenant compte de leur impact environnemental. Nous croyons que prendre soin de sa santé ne devrait pas se faire au détriment de notre planète.
        </p>
        <p className="text-gray-700">
          En évaluant chaque produit selon des critères environnementaux stricts, nous vous permettons de choisir des compléments qui sont non seulement bénéfiques pour votre santé, mais aussi respectueux de l'environnement.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4">Notre Méthodologie</h2>
        <p className="text-gray-700 mb-4">
          Chaque complément alimentaire est évalué selon quatre critères principaux :
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-xl font-medium mb-2">1. Production (30%)</h3>
            <ul className="list-disc pl-5 text-gray-700">
              <li>Émissions de CO2 lors de la fabrication</li>
              <li>Consommation d'eau</li>
              <li>Utilisation de solvants toxiques</li>
              <li>Source des matières premières</li>
              <li>Distance de transport des composants</li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-xl font-medium mb-2">2. Emballage (20%)</h3>
            <ul className="list-disc pl-5 text-gray-700">
              <li>Type de matériaux utilisés</li>
              <li>Volume d'emballage par rapport au produit</li>
              <li>Possibilité de réutilisation</li>
              <li>Encres et additifs utilisés</li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-xl font-medium mb-2">3. Élimination (30%)</h3>
            <ul className="list-disc pl-5 text-gray-700">
              <li>Biodégradabilité du principe actif</li>
              <li>Impact sur les écosystèmes aquatiques</li>
              <li>Persistance dans l'environnement</li>
              <li>Métabolites toxiques</li>
              <li>Méthode d'élimination recommandée</li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-xl font-medium mb-2">4. Cycle de vie (20%)</h3>
            <ul className="list-disc pl-5 text-gray-700">
              <li>Durée de conservation</li>
              <li>Conditions de stockage</li>
              <li>Fréquence d'administration</li>
              <li>Transport jusqu'au point de vente</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4">Les Notes</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Note</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Impact environnemental</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    A
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">80-100%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Excellent impact environnemental</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    B
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">60-79%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Bon impact</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                    C
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">40-59%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Impact modéré</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-orange-100 text-orange-800">
                    D
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">20-39%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Impact significatif</td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                    E
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">0-19%</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Impact très élevé</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;