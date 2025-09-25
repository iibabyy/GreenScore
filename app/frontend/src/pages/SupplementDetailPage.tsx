import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Supplement } from '../lib/types';
import RatingDisplay from '../components/RatingDisplay';
import EnvironmentalMetrics from '../components/EnvironmentalMetrics';

// Données de démonstration
const mockSupplement: Supplement = {
  id: '1',
  name: 'Vitamine C',
  brand: 'Nature\'s Best',
  description: 'Complexe de vitamine C avec bioflavonoïdes. La vitamine C est un antioxydant essentiel qui contribue au fonctionnement normal du système immunitaire et à la réduction de la fatigue.',
  ingredients: ['Vitamine C (acide ascorbique)', 'Bioflavonoïdes d\'agrumes', 'Cellulose microcristalline', 'Stéarate de magnésium'],
  dosage: '1 comprimé par jour, de préférence avec un repas',
  environmentalScore: 75,
  letterScore: 'B',
  carbonFootprint: 2.5,
  waterUsage: 150,
  packagingScore: 4,
  certifications: ['organic'],
  createdAt: '2023-01-01',
  updatedAt: '2023-01-01'
};

const SupplementDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [isFavorite, setIsFavorite] = useState(false);

  // Dans une vraie application, on récupérerait le complément via une API
  // const supplement = useSupplement(id);
  const supplement = mockSupplement;

  // Utilisation de la variable id pour éviter l'erreur TS6133
  console.log('ID du complément:', id);

  const toggleFavorite = () => {
    setIsFavorite(!isFavorite);
    // Dans une vraie application, on appellerait une API pour sauvegarder le favori
  };

  if (!supplement) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <p className="text-xl text-gray-600">Complément non trouvé</p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{supplement.name}</h1>
            <p className="text-xl text-gray-600">{supplement.brand}</p>
          </div>
          <button 
            onClick={toggleFavorite}
            className={`mt-4 md:mt-0 px-4 py-2 rounded-full flex items-center ${
              isFavorite 
                ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-5 w-5 mr-1" 
              viewBox="0 0 20 20" 
              fill={isFavorite ? "currentColor" : "none"} 
              stroke="currentColor"
            >
              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
            </svg>
            {isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
          </button>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Description</h2>
          <p className="text-gray-700">{supplement.description}</p>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Ingrédients</h2>
          <ul className="list-disc pl-5 text-gray-700">
            {supplement.ingredients.map((ingredient, index) => (
              <li key={index}>{ingredient}</li>
            ))}
          </ul>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Dosage recommandé</h2>
          <p className="text-gray-700">{supplement.dosage}</p>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Évaluation environnementale</h2>
          <div className="flex flex-col md:flex-row gap-8">
            <div className="md:w-1/3">
              <RatingDisplay 
                score={supplement.environmentalScore} 
                letter={supplement.letterScore} 
              />
            </div>
            <div className="md:w-2/3">
              <EnvironmentalMetrics supplement={supplement} />
            </div>
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Certifications</h2>
          <div className="flex flex-wrap gap-2">
            {supplement.certifications.map((cert, index) => (
              <span 
                key={index} 
                className="bg-accent text-gray-800 px-3 py-1 rounded-full text-sm"
              >
                {cert}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupplementDetailPage;