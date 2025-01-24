# Founder Insights

An AI agent project that enriches and verifies founder information against Wikipedia data. The system takes founder data from a structured CSV input, verifies and enhances it with Wikipedia information, and provides detailed profiles including education, career history, and achievements.

## Tech Stack

- **Python 3.12+**
- **Libraries**:
  - `langchain`: For AI-powered text processing and verification
  - `wikipedia`: Wikipedia API integration
  - `beautifulsoup4`: Web scraping and HTML parsing
  - `requests`: HTTP requests handling
  - `pandas`: Data manipulation and CSV handling
  - `python-dotenv`: Environment variable management

## Features

- **Input Processing**: Takes founder information from a structured CSV file.
- **Wikipedia Verification**: Validates and enriches founder information using Wikipedia data
- **Structured Data Storage**: 
  - JSON storage with detailed founder profiles
  - CSV export with flattened data structure
- **Progress Tracking**: Maintains processing state for long-running operations
- **Rich Data Fields**:
  - Education details (degree, institution, field)
  - Career history with multiple experiences
  - Current role information
  - Achievements and responsibilities
  - Source URLs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ice_breaker.git
cd ice_breaker
```

2. Install dependencies using pipenv:
```bash
pip install pipenv
pipenv install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your API keys and configurations
```

## Usage

1. **Prepare Input Data**:
   Create a CSV file following the structure with these column names:
   Founder Name,
   Title,
   Company Founded,
   Description,
   LinkedIn Profile,
   Twitter Profile

2. **Process Founder Data**:
```bash
pipenv run python agents/process_founders.py
```

3. **Convert JSON to CSV**:
```bash
pipenv run python scripts/json_to_csv_converter.py
```

4. **Verify Wikipedia Information**:
```bash
pipenv run python agents/wikipedia_lookup_agent.py
```

## Data Structure

### JSON Format
```json
{
  "founder_name": {
    "short_description": "...",
    "education": {
      "degree": "...",
      "institution": "...",
      "field": "..."
    },
    "career": {
      "current_role": {
        "title": "...",
        "company": "...",
        "description": "...",
        "duration": "...",
        "achievements": []
      },
      "experience": [],
      "total_years_experience": "..."
    },
    "source_url": "..."
  }
}
```

### CSV Format
The CSV output includes flattened columns for:
- Basic information (name, description)
- Education details
- Current role information
- Up to 7 past experiences with details
- Source URLs

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.# founders-insights
