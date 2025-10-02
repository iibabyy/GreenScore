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
  const [evaluationLength, setEvaluationLength] = useState<number | null>(null);
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
              setEvaluationLength(evalData?.debug_info?.evaluation_length ?? null);
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
                  setEvaluationLength(data?.debug_info?.evaluation_length ?? null);
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