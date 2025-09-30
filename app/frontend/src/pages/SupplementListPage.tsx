import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import SupplementCard from '../components/SupplementCard';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';
import { Supplement } from '../lib/types';

// Les données sont maintenant récupérées dynamiquement depuis le backend

const SupplementListPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredSupplements, setFilteredSupplements] = useState<Supplement[]>([]);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetchSupplements(term);
    }, 200); // 200ms debounce pour plus de réactivité
  };

  const fetchSupplements = async (term: string) => {
    try {
      const cacheKey = `search_${term.toLowerCase().trim()}`;
      
      // Vérifier le cache localStorage d'abord
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        const isExpired = Date.now() - timestamp > 5 * 60 * 1000; // 5 minutes
        
        if (!isExpired) {
          console.log(`Cache frontend hit pour: "${term}"`);
          setFilteredSupplements(data.results || []);
          return;
        } else {
          localStorage.removeItem(cacheKey);
        }
      }

      // Sinon, faire l'appel API
      const res = await fetch(`/api/search?query=${encodeURIComponent(term)}`);
      if (!res.ok) throw new Error('Erreur API');
      const data = await res.json();
      
      // Mettre en cache le résultat
      localStorage.setItem(cacheKey, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
      
      setFilteredSupplements(data.results || []);
    } catch (err) {
      setFilteredSupplements([]);
    }
  };


  // Initial fetch (optionnel, pour afficher des suggestions au chargement)
  useEffect(() => {
    fetchSupplements('');
  }, []);

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
                  fetchSupplements('');
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