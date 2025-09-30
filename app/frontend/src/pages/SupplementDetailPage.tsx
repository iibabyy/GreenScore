import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Supplement } from '../lib/types';
import RatingDisplay from '../components/RatingDisplay';
import EnvironmentalMetrics from '../components/EnvironmentalMetrics';
import MrGreenCard from '../components/MrGreenCard';

const SupplementDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [isFavorite, setIsFavorite] = useState(false);
  const [supplement, setSupplement] = useState<Supplement | null>(null);
  const [loading, setLoading] = useState(false);
  const [mrGreenAnswer, setMrGreenAnswer] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Utilisation de la variable id pour éviter l'erreur TS6133
  console.log('ID du complément:', id);

  const toggleFavorite = () => {
    setIsFavorite(!isFavorite);
    // Dans une vraie application, on appellerait une API pour sauvegarder le favori
  };

  useEffect(() => {
    let mounted = true;

    const fetchProductAndEvaluate = async () => {
      try {
        setLoading(true);
        setError(null);

        // 1) Essayer de récupérer le produit via un endpoint dédié
        let product: Supplement | null = null;

        try {
          const res = await fetch(`/api/product/${encodeURIComponent(id || '')}`);
          if (res.ok) {
            product = await res.json();
          }
        } catch (e) {
          // ignore - fallback to search
        }

        // 2) Fallback: utiliser le endpoint search pour retrouver le produit
        if (!product) {
          const res2 = await fetch(`/api/search?query=${encodeURIComponent(id || '')}`);
          if (res2.ok) {
            const data = await res2.json();
            const results = data.results || [];
            product = results.find((p: Supplement) => String(p.id) === String(id)) || results[0] || null;
          }
        }

        if (!product) {
          setSupplement(null);
          setError('Produit introuvable');
          setLoading(false);
          return;
        }

        if (!mounted) return;
        setSupplement(product);

        // 3) Appeler le backend pour évaluer le produit via AI
        const callEvaluate = async () => {
          try {
            setLoading(true);
            setError(null);
            setMrGreenAnswer(null);

            const evalRes = await fetch('/api/evaluate-product', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(product)
            });

            if (!evalRes.ok) {
              const txt = await evalRes.text();
              console.error('Evaluate API error:', evalRes.status, txt);
              setError('Erreur du service d\'évaluation');
              setMrGreenAnswer(null);
            } else {
              const evalData = await evalRes.json();
              const text = evalData.evaluation || evalData.answer || JSON.stringify(evalData);
              setMrGreenAnswer(String(text));
            }
          } catch (e) {
            console.error('Erreur appel evaluate-product:', e);
            setError('Erreur réseau lors de l\'appel à Mr Green');
            setMrGreenAnswer(null);
          } finally {
            setLoading(false);
          }
        };

        await callEvaluate();

      } catch (err) {
        console.error('Erreur chargement detail produit:', err);
        setError('Erreur lors du chargement');
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchProductAndEvaluate();

    return () => { mounted = false; };
  }, [id]);

  if (error) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <p className="text-xl text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!supplement || loading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-20">
          <div className="inline-flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-accent animate-pulse flex items-center justify-center text-white font-bold">MG</div>
            <div className="text-left">
              <p className="text-lg font-semibold">Mr Green réfléchit...</p>
              <p className="text-sm text-gray-500">Analyse en cours — ceci peut prendre quelques secondes</p>
            </div>
          </div>
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
      {/* Mr Green response card */}
      <div>
        <MrGreenCard
          text={mrGreenAnswer}
          loading={loading}
          error={error}
          onRetry={() => {
            // retry: re-run the evaluate call
            (async () => {
              if (!supplement) return;
              setError(null);
              setLoading(true);
              try {
                const res = await fetch('/api/evaluate-product', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(supplement)
                });
                if (!res.ok) {
                  setError('Erreur du service d\'évaluation (retry)');
                } else {
                  const data = await res.json();
                  setMrGreenAnswer(data.evaluation || data.answer || JSON.stringify(data));
                }
              } catch (e) {
                setError('Erreur réseau lors du retry');
              } finally {
                setLoading(false);
              }
            })();
          }}
        />
      </div>
    </div>
  );
};

export default SupplementDetailPage;