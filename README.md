# OsintSpector - Final Year Project (TFG)

This project was developed as part of my **Final Year Project (TFG)** for my university degree in "Ingeniería Informática - Tecnologías Informáticas" with an specialization in "Tecnologías de la Información" at the University of Seville (Universidad de Sevilla-España, US). The complete project thesis can be found [here](./TFG_memoria.pdf).

**OsintSpector** is an open-source intelligence (OSINT) tool that enables the collection and analysis of public data. It offers two core investigation modules, along with a user-friendly interface.

## Features

### 1. Public Information Search
This module focuses on gathering information about individuals using several OSINT tools. Below are the tools integrated into this module:

- **Darknet Search (AhmiaScraping)**: Searches for information in the Darknet using the Ahmia search engine and returns relevant results about the target.
  
- **Email and Phone Lookup (HIBP API & IntelX)**: Utilizes the *Have I Been Pwned (HIBP)* and *IntelX* APIs to identify email breaches, pastes, and phone numbers linked to the target. This information provides insights into where sensitive data may have been compromised.

- **Person Search in Search Engines (GoogleScrapingPerson)**: Gathers results about a person’s name and surname from search engines like Google and produces a word cloud and chart of the findings.

- **Username Scraping**: Searches for usernames across multiple websites by leveraging precompiled lists of known sites and matches. It identifies accounts tied to a specific username and provides insights into a person’s online presence.

### 2. Twitter Investigation Module
This module conducts in-depth investigations using Twitter handles. Features include:

- **Tweet Scraping**: Extracts a set number of tweets and filters relevant information.
- **Word Cloud Generation**: Processes tweet data and generates a visual representation of common words.
- **User Interaction Graphs**: Creates graphs showing interactions between users based on mentions.
- **Sentiment Analysis**: Applies machine learning models to analyze the emotional content of tweets.
- **Location Tracking**: Tracks location data embedded in tweets and maps them.
- **Community Analysis**: Visualizes user interaction networks and analyzes community structures.

### User Interface and Dashboard
OsintSpector features a sleek and accessible web-based interface powered by Flask. Users can input data and analyze results using an interactive dashboard. The dashboard displays visualizations such as word clouds, graphs, sentiment analysis, and community breakdowns, making the raw data actionable and easy to interpret.

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/juanluidos/OsintSpector.git
    cd OsintSpector
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables (e.g., API keys for HIBP and IntelX) in a `.env` file.

4. Run the Flask application:
    ```bash
    flask run
    ```

## Usage

- Open the web interface in a browser by navigating to the local server.
- Enter either a person’s information or a Twitter handle to perform the investigation.
- The results, including visualizations and raw data analysis, are available in the dashboard for further interpretation.

## Technologies Used
- **Flask**: Backend and web interface.
- **Python**: Primary programming language.
- **Snscrape**: Scraping tool for Twitter data.
- **Pandas**: Data manipulation and analysis.
- **Numpy**: Numerical processing.
- **WordCloud**: Textual word cloud generation.
- **NetworkX**: Network and community graph analysis.
- **Transformers**: Sentiment analysis.
- **Playwright**: Scraping engine for websites.

## License
This project is licensed under the MIT License.
