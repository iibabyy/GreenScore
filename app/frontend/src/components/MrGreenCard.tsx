import React, { useMemo } from 'react';

interface MrGreenCardProps {
  text: string | null;
  loading: boolean;
  onRetry?: () => void;
  error?: string | null;
}

import useWordReveal from '../hooks/useWordReveal';

// Simple markdown token stripper for **bold**, *italic*, backticks
function stripSimpleMarkdown(src: string): string {
  return src
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/__([^_]+)__/g, '$1')
    .replace(/\[(.*?)\]\((.*?)\)/g, '$1');
}

const MrGreenCard: React.FC<MrGreenCardProps> = ({ text, loading, onRetry, error }) => {
  const cleaned = useMemo(() => (text ? stripSimpleMarkdown(text) : ''), [text]);
  const revealed = useWordReveal(cleaned);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex gap-5 max-w-2xl mx-auto">
      <div className="flex-shrink-0">
        <div className="w-14 h-14 rounded-full bg-green-600 flex items-center justify-center text-white font-semibold text-lg">MG</div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-medium tracking-wide text-gray-700">Mr Green</h3>
          {loading && <div className="text-xs text-gray-500">Analyse en cours...</div>}
        </div>
        <div className="mt-2">
          {error ? (
            <div className="text-red-600 text-sm whitespace-pre-wrap">
              <p>{error}</p>
              {onRetry && (
                <button onClick={onRetry} className="mt-2 inline-block bg-accent text-gray-900 py-1 px-3 rounded text-xs">Réessayer</button>
              )}
            </div>
          ) : loading ? (
            <div className="animate-pulse">
              <div className="h-3.5 bg-gray-200 rounded mb-2 w-4/5" />
              <div className="h-3.5 bg-gray-200 rounded mb-2 w-3/5" />
              <div className="h-3.5 bg-gray-200 rounded w-2/3" />
            </div>
          ) : cleaned ? (
            <div
              className="text-sm leading-6 text-gray-800 font-normal whitespace-pre-wrap break-words transition-all"
              aria-label="Mr Green réponse"
            >
              {revealed}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">Aucune évaluation disponible.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default MrGreenCard;
