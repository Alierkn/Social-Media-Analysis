# MQTT Social Big Data Analysis

A system that performs big data analysis and storage across different database platforms using MQTT Server and Python. It also includes social media analysis functionality for Twitter and Reddit platforms.

[![GitHub license](https://img.shields.io/github/license/Alierkn/Social-Media-Analysis)](https://github.com/Alierkn/Social-Media-Analysis/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Alierkn/Social-Media-Analysis)](https://github.com/Alierkn/Social-Media-Analysis/stargazers)

## Overview

This project integrates IoT sensor data with social media analysis to provide comprehensive insights. It uses MQTT for real-time data collection, stores data in multiple database types (SQL, MongoDB, Neo4j), and provides analytics capabilities for both sensor data and social media content.

## Project Structure
```
mqtt-social-bigdata/
├── config/                    # Configuration files
├── src/                      # Source code
│   ├── mqtt_client.py        # MQTT client
│   ├── database_manager.py   # Database manager
│   ├── social_media_connector.py # Social media API connection
│   ├── data_processor.py     # Data processing module
│   └── utils/                # Utility tools
├── scripts/                  # Scripts
│   ├── setup_databases.py    # Database setup script
│   └── generate_test_data.py # Test data generation
├── main.py                   # Main application
├── requirements.txt          # Dependencies
├── Dockerfile               # Docker configuration
└── docker-compose.yml       # Docker Compose configuration
```

## Installation

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional, but recommended)
- MQTT Broker (Mosquitto)
- MongoDB
- Neo4j

### Step 1: Clone the Project

```bash
git clone https://github.com/Alierkn/Social-Media-Analysis.git
cd Social-Media-Analysis
```

### Step 2: Set Up Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the `config/.env.example` file to `.env` and add your credentials:

```bash
cp config/.env.example .env
# Edit the .env file
```

### Step 5: Set Up Databases

```bash
# With Docker (recommended)
docker-compose up -d

# or
python scripts/setup_databases.py
```

## Usage

### Running the Application

```bash
# With Docker
docker-compose up -d app

# or directly with Python
python main.py
```

### Generating Test Data

```bash
python scripts/generate_test_data.py
```

## Features

- Collects IoT data over MQTT protocol
- Retrieves social media data through Twitter and Reddit APIs
- Performs sentiment analysis on data
- Identifies influencer users and conversation trends
- Stores data in SQL, MongoDB, and Neo4j databases
- Generates daily reports

## Development Steps

1. Create the necessary directories
2. Add basic configuration files: requirements.txt, .env, .gitignore, README.md
3. Set up MQTT client and database connections
4. Integrate social media connectivity
5. Develop data processing logic
6. Complete Docker configuration
7. Generate and test with sample data

After setting up the project structure, you can enhance the code and particularly expand the social media analysis component.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Ali Erkan Oca**
- GitHub: [Alierkn](https://github.com/Alierkn)

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- MQTT Protocol for enabling lightweight IoT communication
- Twitter and Reddit APIs for social media data access
- Docker and Docker Compose for containerization
- All the open-source libraries that made this project possible
