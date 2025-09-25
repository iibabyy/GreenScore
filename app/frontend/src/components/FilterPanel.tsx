const FilterPanel = () => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Filtres</h2>
      
      <div className="space-y-6">
        <div>
          <h3 className="font-medium text-gray-900 mb-2">Marque</h3>
          <div className="space-y-2">
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">Nature's Best</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">Océan Health</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">BioLife</span>
            </label>
          </div>
        </div>
        
        <div>
          <h3 className="font-medium text-gray-900 mb-2">Note environnementale</h3>
          <div className="space-y-2">
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">A (Excellent)</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">B (Bon)</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">C (Modéré)</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">D (Significatif)</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">E (Très élevé)</span>
            </label>
          </div>
        </div>
        
        <div>
          <h3 className="font-medium text-gray-900 mb-2">Certifications</h3>
          <div className="space-y-2">
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">Organic</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">Vegan</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" className="rounded text-accent focus:ring-accent" />
              <span className="ml-2 text-gray-700">Sustainable</span>
            </label>
          </div>
        </div>
        
        <button className="w-full bg-accent text-gray-900 font-medium py-2 px-4 rounded hover:bg-secondary transition-colors">
          Appliquer les filtres
        </button>
      </div>
    </div>
  );
};

export default FilterPanel;