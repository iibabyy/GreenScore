import express from 'express';

const router = express.Router();

// GET /api/health
router.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'GreenScore API is running' });
});

export default router;