# GreenScore ♻️

GreenScore is a full-stack application that helps users discover the environmental impact of pharmaceutical products, such as dietary supplements and medications. The goal is to enable consumers to make informed choices to reduce their carbon footprint based on the products they consume. GreenScore was developed for the Doctolib AI Hackathon, with a focus on environmental sustainability. It leverages the Mistral AI API to analyze products and provide detailed environmental insights.

## Features
- Pharmaceutical Product Search: Search and compare pharmaceutical products based on their environmental impact
- Product Ranking: Products are ranked from least to most polluting based on predefined criteria
- Detailed Product Insights: Users can obtain detailed environmental impact information for each product via an integrated chatbot
- Product Comparison: Compare two specific products to analyze their environmental impact differences

## Prerequisites
- Docker
- Docker Compose
- Git
- Make

## Installation
```bash
# Clone repository
git clone https://github.com/your_username/GreenScore.git
cd GreenScore

# Start application
make
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

## Documentation

### Quick Start
```bash
# Clone repository
git clone https://github.com/your_username/GreenScore.git
cd GreenScore

# Start application
make

# Access application
Frontend: http://localhost:8080
Backend: http://localhost:8000
```

### Features
- Product environmental impact search
- Comparative analysis
- Interactive chat interface
- Detailed impact reports
- Product recommendations

### Architecture

#### Frontend
- HTML/CSS (Tailwind)
- Vanilla JavaScript
- Responsive design

#### Backend
- FastAPI REST API
- JSON data storage
- Environmental impact calculation engine

### API Endpoints
```
GET /products/search/{search}  # Search products
GET /products/{id}            # Get product details
POST /products               # Create new product
```

### Environmental Impact Scoring
Products are scored (0-5) based on:
- Persistence in environment
- Bioaccumulation
- Toxicity
- Ecological effects
- Degradation byproducts
- Release patterns
- Regulatory status

### Development Commands
```bash
make         # Start application
make down    # Stop application
make log     # View logs
make re      # Restart application
```

### Troubleshooting
- Port conflicts: Modify ports in docker-compose.yml
- Container issues: Check logs with `make log`
- Build errors: Clear Docker cache and rebuild

## Usage
1. Visit http://localhost:8080 in your web browser
2. Use the search bar to enter the name of a supplement or medication
3. The system will display a list of products ranked from least to most polluting
4. Click "Learn More" to access a chatbot that explains why a product received a specific environmental rating
5. Users can also compare two products to identify their environmental impact differences

## Development
To run the application in development mode:
```bash
# Start with hot-reload enabled
make

# View logs
make log

# Restart the application
make re
```

## Acknowledgments
- Doctolib AI Hackathon organizers
- Mistral AI for their API
- All contributors and supporters
