GreenScore

GreenScore is a full-stack application that helps users discover the environmental impact of pharmaceutical products, such as dietary supplements and medications. The goal is to enable consumers to make informed choices to reduce their carbon footprint based on the products they consume. GreenScore was developed for the Doctolib AI Hackathon, with a focus on environmental sustainability. It leverages the Mistral AI API to analyze products and provide detailed environmental insights.

Features

Pharmaceutical Product Search: Search and compare pharmaceutical products (supplements, medications) based on their environmental impact.

Product Ranking: Products are ranked from least to most polluting based on predefined criteria.

Detailed Product Insights: Users can obtain detailed environmental impact information for each product via an integrated chatbot.

Product Comparison: Compare two specific products to analyze their environmental impact differences.

Installation

Clone this repository to your local machine:

git clone https://github.com/your_username/GreenScore.git

Open the index.html file in a local server emulator (e.g., using Live Server on Visual Studio Code) to test the application locally. The project is not yet hosted online.

Usage

Visit the website and use the search bar to enter the name of a supplement or medication.

The system will display a list of products ranked from least to most polluting.

Click "Learn More" to access a chatbot that explains why a product received a specific environmental rating.

Users can also compare two products to identify their environmental impact differences.

Environmental Impact Assessment

GreenScore utilizes the Barem Framework, which evaluates the environmental impact of pharmaceutical products based on key factors such as:

Persistence: How long a drug remains in the environment.

Bioaccumulation: The tendency of a drug to accumulate in living organisms.

Toxicity: Harmful effects on ecosystems and wildlife.

Ecotoxicological Effects: Disruptions to specific species or habitats.

Degradation Byproducts: Harmful substances released when a drug breaks down.

Release into the Environment: How a drug enters and affects ecosystems.

Regulatory Status: Legal oversight regarding environmental impact.

Each factor is scored from 0 (no impact) to 5 (severe impact), and a weighted average provides an overall environmental score.

Contribution

The project is developed by BrokenTeam as part of the Doctolib AI Hackathon. If you wish to contribute or improve the application, feel free to open an issue or submit a pull request.

License

This project is licensed under the MIT License – see the LICENSE file for details.
