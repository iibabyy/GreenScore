import { scoreStyle } from '../lib/scoreStyles';

const RatingDisplay = ({ score, letter }: { score: number; letter: string }) => {
  const style = scoreStyle(letter);

  // Calculer le pourcentage pour le cercle
  const percentage = score;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-48 mb-4">
        {/* Cercle de fond */}
        <div className="absolute inset-0 rounded-full border-8 border-gray-200"></div>
        
        {/* Cercle de progression */}
        <div 
          className="absolute inset-0 rounded-full border-8 border-current"
          style={{
            borderColor: letter === 'A' ? '#10B981' : 
                        letter === 'B' ? '#3B82F6' : 
                        letter === 'C' ? '#F59E0B' : 
                        letter === 'D' ? '#F97316' : '#EF4444',
            clipPath: `inset(0 ${100 - percentage}% 0 0)`
          }}
        ></div>
        
        {/* Contenu du cercle */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${style.primary}`}>
            {letter}
          </span>
          <span className="text-lg text-gray-600">{score}/100</span>
        </div>
      </div>
      
  <div className={`px-6 py-2 rounded-full border ${style.badge} text-lg font-semibold`}>
        {letter === 'A' && 'Excellent impact environnemental'}
        {letter === 'B' && 'Bon impact'}
        {letter === 'C' && 'Impact modéré'}
        {letter === 'D' && 'Impact significatif'}
        {letter === 'E' && 'Impact très élevé'}
      </div>
    </div>
  );
};

export default RatingDisplay;