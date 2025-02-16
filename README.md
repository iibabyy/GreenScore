# GreenScore

GreenScore is a full-stack application that helps users discover the environmental impact of pharmaceutical products, such as dietary supplements and medications. The goal is to enable consumers to make informed choices to reduce their carbon footprint based on the products they consume. GreenScore was developed for the Doctolib AI Hackathon, with a focus on environmental sustainability. It leverages the Mistral AI API to analyze products and provide detailed environmental insights.

## Features

- **Pharmaceutical Product Search**: Search and compare pharmaceutical products (supplements, medications) based on their environmental impact.
- **Product Ranking**: Products are ranked from least to most polluting based on predefined criteria.
- **Detailed Product Insights**: Users can obtain detailed environmental impact information for each product via an integrated chatbot.
- **Product Comparison**: Compare two specific products to analyze their environmental impact differences.

## Prerequisites

- Docker
- Docker Compose
- Git
- Make

## Installation

1. Clone this repository to your local machine:
```bash
git clone https://github.com/your_username/GreenScore.git
cd GreenScore
```

2. Start the application using Make:
```bash
make
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

## Make Commands

- `make`: Start the application
- `make down`: Stop the application
- `make log`: View application logs
- `make re`: Restart the application
- Use `Ctrl + C` to stop the application while running in foreground

## Usage

1. Visit http://localhost:8080 in your web browser
2. Use the search bar to enter the name of a supplement or medication
3. The system will display a list of products ranked from least to most polluting
4. Click "Learn More" to access a chatbot that explains why a product received a specific environmental rating
5. Users can also compare two products to identify their environmental impact differences

## Environmental Impact Assessment

GreenScore utilizes the Barem Framework, which evaluates the environmental impact of pharmaceutical products based on key factors such as:

1. **Persistence**: How long a drug remains in the environment
2. **Bioaccumulation**: The tendency of a drug to accumulate in living organisms
3. **Toxicity**: Harmful effects on ecosystems and wildlife
4. **Ecotoxicological Effects**: Disruptions to specific species or habitats
5. **Degradation Byproducts**: Harmful substances released when a drug breaks down
6. **Release into the Environment**: How a drug enters and affects ecosystems
7. **Regulatory Status**: Legal oversight regarding environmental impact

Each factor is scored from 0 (no impact) to 5 (severe impact), and a weighted average provides an overall environmental score.

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

## Troubleshooting

Common issues and their solutions:

1. If ports 8080 or 8000 are already in use:
   - Modify the ports in `docker-compose.yml`
   - Stop any services using these ports

2. If containers fail to start:
   ```bash
   # View logs
   make log

   # Restart the application
   make re
   ```
