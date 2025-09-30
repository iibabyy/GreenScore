import React from 'react';
import ReactMarkdown from 'react-markdown';

interface MrGreenCardProps {
  text: string | null;
  loading: boolean;
  onRetry?: () => void;
  error?: string | null;
}

const MrGreenCard: React.FC<MrGreenCardProps> = ({ text, loading, onRetry, error }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex gap-6">
      <div className="flex-shrink-0">
        <div className="w-16 h-16 rounded-full bg-green-600 flex items-center justify-center text-white font-bold text-xl">MG</div>
      </div>
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Mr Green</h3>
          {loading && <div className="text-sm text-gray-500">Analyse en cours...</div>}
        </div>

        <div className="mt-3">
          {error ? (
            <div className="text-red-600">
              <p>{error}</p>
              {onRetry && (
                <button onClick={onRetry} className="mt-2 inline-block bg-accent text-gray-900 py-1 px-3 rounded">Réessayer</button>
              )}
            </div>
          ) : loading ? (
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2 w-3/4" />
              <div className="h-4 bg-gray-200 rounded mb-2 w-5/6" />
              <div className="h-4 bg-gray-200 rounded w-2/3" />
            </div>
          ) : text ? (
            <div className="prose text-gray-800">
              <ReactMarkdown>{text}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-gray-500">Aucune évaluation disponible.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MrGreenCard;
