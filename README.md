# MQTT Social Big Data Analysis

A system that performs big data analysis and storage across different database platforms using MQTT Server and Python. It also includes social media analysis functionality.

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
git clone https://github.com/username/mqtt-social-bigdata.git
cd mqtt-social-bigdata
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
