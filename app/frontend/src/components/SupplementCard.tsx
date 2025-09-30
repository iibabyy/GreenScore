import { Supplement } from '../lib/types';

interface SupplementCardProps {
  supplement: Supplement;
}

const SupplementCard: React.FC<SupplementCardProps> = ({ supplement }) => {
  // Déterminer la couleur en fonction de la note
  const getScoreColor = (letter: string) => {
    switch (letter) {
      case 'A': return 'bg-green-100 text-green-800';
      case 'B': return 'bg-blue-100 text-blue-800';
      case 'C': return 'bg-yellow-100 text-yellow-800';
      case 'D': return 'bg-orange-100 text-orange-800';
      case 'E': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      {supplement.imageUrl && (
        <div className="h-48 w-full overflow-hidden">
          <img 
            src={supplement.imageUrl} 
            alt={supplement.name}
            className="h-full w-full object-cover"
            onError={(e) => {
              // Masquer l'image si elle ne peut pas être chargée
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      )}
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">{supplement.name}</h3>
            <p className="text-gray-600">{supplement.brand}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(supplement.letterScore)}`}>
            {supplement.letterScore}
          </span>
        </div>
        
        <p className="text-gray-700 mb-4 line-clamp-3">{supplement.description}</p>
        
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-5 w-5 text-gray-400 mr-1" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-gray-600">{supplement.environmentalScore}/100</span>
          </div>
          
          <div className="flex items-center">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-5 w-5 text-gray-400 mr-1" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-gray-600">{supplement.dosage}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupplementCard;