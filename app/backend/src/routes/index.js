import express from 'express';
import fetch from 'node-fetch';

const router = express.Router();

// Rate limiting pour Open Food Facts (10 req/min pour /search)
let lastSearchTime = 0;
const SEARCH_RATE_LIMIT = 6000; // 6 secondes entre les requêtes pour respecter 10/min

// Cache en mémoire pour les résultats de recherche
const searchCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes de cache

// GET /api/health
router.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'GreenScore API is running' });
});

// POST /api/evaluate-product - forward product description to AI service
router.post('/evaluate-product', async (req, res) => {
  try {
    const product = req.body;

    if (!product || !product.description) {
      return res.status(400).json({ error: 'Missing product or product.description' });
    }

    // URL de l'AI service - en dev via proxy/docker-compose
    const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:5000/api/evaluate';

    // FastAPI endpoint expects product_description as a query parameter (Query(...)).
    const urlWithQuery = `${aiUrl}?product_description=${encodeURIComponent(product.description)}`;

    const aiResponse = await fetch(urlWithQuery, {
      method: 'POST'
    });

    if (!aiResponse.ok) {
      const text = await aiResponse.text();
      console.error('AI service error:', aiResponse.status, text);
      return res.status(502).json({ error: 'AI service error', details: text });
    }

    const data = await aiResponse.json();
    // Forward the AI response to frontend
    res.json(data);
  } catch (err) {
    console.error('Error in /evaluate-product proxy:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/search - Recherche dans Open Food Facts
router.get('/search', async (req, res) => {
  try {
    const { query } = req.query;
    
    if (!query || query.trim() === '') {
      return res.json({ results: [] });
    }

    const searchKey = query.toLowerCase().trim();
    
    // Vérifier le cache d'abord
    if (searchCache.has(searchKey)) {
      const cached = searchCache.get(searchKey);
      if (Date.now() - cached.timestamp < CACHE_DURATION) {
        console.log(`Cache hit pour: "${searchKey}"`);
        return res.json(cached.data);
      } else {
        // Supprimer les entrées expirées
        searchCache.delete(searchKey);
      }
    }

    // Rate limiting
    const now = Date.now();
    const timeSinceLastSearch = now - lastSearchTime;
    
    if (timeSinceLastSearch < SEARCH_RATE_LIMIT) {
      const waitTime = SEARCH_RATE_LIMIT - timeSinceLastSearch;
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    lastSearchTime = Date.now();

    // Appel à l'API Open Food Facts avec champs optimisés
    const fields = 'code,product_name,product_name_fr,brands,generic_name,categories,ingredients_text,image_url,image_front_url,nutrition_grades,nutriscore_grade,ecoscore_grade,ecoscore_data,labels,packaging_score';
    const searchUrl = `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&json=1&page_size=15&fields=${fields}`;
    
    const response = await fetch(searchUrl, {
      headers: {
        'User-Agent': 'GreenScore/1.0.0 (contact@greenscore.app)'
      }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    const data = await response.json();
    
    // Transformer les données Open Food Facts en format GreenScore
    const transformedResults = (data.products || []).map(product => ({
      id: product.code || product._id,
      name: product.product_name || product.product_name_fr || 'Produit sans nom',
      brand: product.brands || 'Marque inconnue',
      description: product.generic_name || product.categories || 'Aucune description',
      ingredients: product.ingredients_text ? 
        product.ingredients_text.split(',').map(ing => ing.trim()).slice(0, 5) : 
        [],
      dosage: 'Voir emballage',
      environmentalScore: calculateEnvironmentalScore(product),
      letterScore: getLetterScore(product),
      carbonFootprint: product.ecoscore_data?.agribalyse?.co2_total || 0,
      waterUsage: 0, // Pas disponible dans Open Food Facts
      packagingScore: product.packaging_score || 3,
      certifications: extractCertifications(product),
      imageUrl: product.image_url || product.image_front_url,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    })).filter(product => product.name !== 'Produit sans nom');

    const resultData = { 
      results: transformedResults,
      total: data.count || 0,
      source: 'Open Food Facts'
    };

    // Mettre en cache les résultats
    searchCache.set(searchKey, {
      data: resultData,
      timestamp: Date.now()
    });

    console.log(`Nouvelle recherche cachée: "${searchKey}" (${transformedResults.length} résultats)`);
    
    res.json(resultData);

  } catch (error) {
    console.error('Erreur lors de la recherche:', error);
    res.status(500).json({ 
      error: 'Erreur lors de la recherche',
      results: []
    });
  }
});

// GET /api/product/:id - Récupère un produit unique depuis Open Food Facts
router.get('/product/:id', async (req, res) => {
  try {
    const { id } = req.params;
    if (!id) return res.status(400).json({ error: 'Missing product id' });

    const productUrl = `https://world.openfoodfacts.org/api/v0/product/${encodeURIComponent(id)}.json`;
    const response = await fetch(productUrl, {
      headers: { 'User-Agent': 'GreenScore/1.0.0 (contact@greenscore.app)' }
    });

    if (!response.ok) {
      console.error('OpenFoodFacts product fetch error:', response.status);
      return res.status(502).json({ error: 'External product API error' });
    }

    const payload = await response.json();
    if (!payload || payload.status !== 1) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const product = payload.product;

    const transformed = {
      id: product.code || id,
      name: product.product_name || product.product_name_fr || 'Produit sans nom',
      brand: product.brands || 'Marque inconnue',
      description: product.generic_name || product.categories || 'Aucune description',
      ingredients: product.ingredients_text ? product.ingredients_text.split(',').map(ing => ing.trim()).slice(0, 10) : [],
      dosage: 'Voir emballage',
      environmentalScore: calculateEnvironmentalScore(product),
      letterScore: getLetterScore(product),
      carbonFootprint: product.ecoscore_data?.agribalyse?.co2_total || 0,
      waterUsage: 0,
      packagingScore: product.packaging_score || 3,
      certifications: extractCertifications(product),
      imageUrl: product.image_url || product.image_front_url,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    res.json(transformed);
  } catch (error) {
    console.error('Erreur lors de la récupération du produit:', error);
    res.status(500).json({ error: 'Erreur interne lors de la récupération du produit' });
  }
});

// Fonction pour calculer un score environnemental basé sur les données Open Food Facts
function calculateEnvironmentalScore(product) {
  let score = 50; // Score de base
  
  // Utiliser l'Ecoscore si disponible
  if (product.ecoscore_grade) {
    const ecoGradeMap = { 'a': 85, 'b': 70, 'c': 55, 'd': 40, 'e': 25 };
    score = ecoGradeMap[product.ecoscore_grade.toLowerCase()] || 50;
  }
  
  // Bonus pour les labels bio/équitable
  const labels = (product.labels || '').toLowerCase();
  if (labels.includes('bio') || labels.includes('organic')) score += 15;
  if (labels.includes('équitable') || labels.includes('fair')) score += 10;
  
  return Math.min(100, Math.max(0, score));
}

// Fonction pour obtenir une note lettre basée sur les scores nutritionnel et environnemental
function getLetterScore(product) {
  const nutriscore = product.nutrition_grades || product.nutriscore_grade;
  const ecoscore = product.ecoscore_grade;
  
  // Prioriser l'ecoscore, sinon nutriscore
  if (ecoscore) return ecoscore.toUpperCase();
  if (nutriscore) return nutriscore.toUpperCase();
  
  return 'C'; // Score par défaut
}

// Fonction pour extraire les certifications des labels
function extractCertifications(product) {
  const certifications = [];
  const labels = (product.labels || '').toLowerCase();
  
  if (labels.includes('bio') || labels.includes('organic')) {
    certifications.push('organic');
  }
  if (labels.includes('équitable') || labels.includes('fair')) {
    certifications.push('fair-trade');
  }
  if (labels.includes('vegan')) {
    certifications.push('vegan');
  }
  if (labels.includes('végétarien') || labels.includes('vegetarian')) {
    certifications.push('vegetarian');
  }
  
  return certifications;
}

export default router;