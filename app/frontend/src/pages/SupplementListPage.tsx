import { useState } from 'react';
import { Link } from 'react-router-dom';
import SupplementCard from '../components/SupplementCard';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';
import { Supplement } from '../lib/types';

// Données de démonstration
const mockSupplements: Supplement[] = [
  {
    id: '1',
    name: 'Vitamine C',
    brand: 'Nature\'s Best',
    description: 'Complexe de vitamine C avec bioflavonoïdes',
    ingredients: ['Vitamine C', 'Bioflavonoïdes', 'Acide ascorbique'],
    dosage: '1000mg par jour',
    environmentalScore: 75,
    letterScore: 'B',
    carbonFootprint: 2.5,
    waterUsage: 150,
    packagingScore: 4,
    certifications: ['organic'],
    createdAt: '2023-01-01',
    updatedAt: '2023-01-01'
  },
  {
    id: '2',
    name: 'Oméga 3',
    brand: 'Océan Health',
    description: 'Huile de poisson sauvage riches en EPA et DHA',
    ingredients: ['Huile de poisson', 'EPA', 'DHA'],
    dosage: '2 capsules par jour',
    environmentalScore: 60,
    letterScore: 'C',
    carbonFootprint: 4.2,
    waterUsage: 200,
    packagingScore: 3,
    certifications: ['sustainable'],
    createdAt: '2023-01-01',
    updatedAt: '2023-01-01'
  },
  {
    id: '3',
    name: 'Probiotiques',
    brand: 'BioLife',
    description: 'Mélange de souches probiotiques pour la flore intestinale',
    ingredients: ['Lactobacillus', 'Bifidobacterium', 'Inuline'],
    dosage: '1 capsule par jour',
    environmentalScore: 85,
    letterScore: 'A',
    carbonFootprint: 1.8,
    waterUsage: 100,
    packagingScore: 5,
    certifications: ['organic', 'vegan'],
    createdAt: '2023-01-01',
    updatedAt: '2023-01-01'
  }
];

const SupplementListPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredSupplements, setFilteredSupplements] = useState<Supplement[]>(mockSupplements);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    if (term.trim() === '') {
      setFilteredSupplements(mockSupplements);
    } else {
      const filtered = mockSupplements.filter(
        supplement => 
          supplement.name.toLowerCase().includes(term.toLowerCase()) ||
          supplement.brand.toLowerCase().includes(term.toLowerCase()) ||
          supplement.ingredients.some(ingredient => 
            ingredient.toLowerCase().includes(term.toLowerCase())
          )
      );
      setFilteredSupplements(filtered);
    }
  };

  // Utilisation de la variable searchTerm pour éviter l'erreur TS6133
  console.log('Terme de recherche:', searchTerm);

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Compléments Alimentaires</h1>
        <SearchBar onSearch={handleSearch} />
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        <div className="md:w-1/4">
          <FilterPanel />
        </div>
        
        <div className="md:w-3/4">
          {filteredSupplements.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-600">Aucun complément trouvé</p>
              <button 
                onClick={() => {
                  setSearchTerm('');
                  setFilteredSupplements(mockSupplements);
                }}
                className="mt-4 text-accent hover:underline"
              >
                Réinitialiser la recherche
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredSupplements.map(supplement => (
                <Link to={`/supplements/${supplement.id}`} key={supplement.id}>
                  <SupplementCard supplement={supplement} />
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SupplementListPage;