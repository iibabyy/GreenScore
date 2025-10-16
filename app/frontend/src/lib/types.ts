export interface Supplement {
  id: string;
  name: string;
  brand: string;
  description: string;
  ingredients: string[];
  dosage: string;
  environmentalScore: number; // 1-100 scale
  letterScore: string; // A, B, C, D, E
  carbonFootprint: number; // in kg CO2
  waterUsage: number; // in liters
  packagingScore: number; // 1-5 scale
  certifications: string[]; // e.g., ["organic", "fair-trade"]
  imageUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface EnvironmentalMetrics {
  carbonFootprint: number;
  waterUsage: number;
  landUsage: number;
  packagingScore: number;
  biodiversityImpact: number;
}

export interface SupplementEvaluation {
  id: string;
  supplementId: string;
  productionScore: number; // 30% weight
  packagingScore: number; // 20% weight
  disposalScore: number; // 30% weight
  lifecycleScore: number; // 20% weight
  overallScore: number;
  letterScore: string;
  createdAt: string;
}