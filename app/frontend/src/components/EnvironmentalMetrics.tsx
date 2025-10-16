import { Supplement } from '../lib/types';

interface EnvironmentalMetricsProps {
  supplement: Supplement;
}

const EnvironmentalMetrics: React.FC<EnvironmentalMetricsProps> = ({ supplement }) => {
  // Données de démonstration pour les métriques détaillées
  const metrics = [
    {
      name: 'Empreinte carbone',
      value: `${supplement.carbonFootprint} kg CO2`,
      description: 'Émissions de gaz à effet de serre lors de la production'
    },
    {
      name: 'Consommation d\'eau',
      value: `${supplement.waterUsage} L`,
      description: 'Volume d\'eau utilisé dans le processus de fabrication'
    },
    {
      name: 'Score d\'emballage',
      value: `${supplement.packagingScore}/5`,
      description: 'Évalué selon la recyclabilité et le volume'
    }
  ];

  return (
    <div>
      <h3 className="text-xl font-semibold mb-4">Métriques environnementales</h3>  
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Conseil d'utilisation</h4>
        <p className="text-sm text-gray-700">
          Pour minimiser l'impact environnemental, privilégiez les produits avec une note A ou B, 
          et respectez le dosage recommandé pour éviter le gaspillage.
        </p>
      </div>
    </div>
  );
};

export default EnvironmentalMetrics;