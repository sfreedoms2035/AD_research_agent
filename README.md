# Automated Driving Research Agent

An AI-powered agent that automatically researches new papers and models in automated driving from the last 7 days. It ranks papers based on quality, impact, innovation, code availability, and summarizes the top papers using advanced AI models.

## Features

- **Automated Research**: Searches for recent papers in autonomous driving
- **Intelligent Ranking**: Ranks papers based on multiple criteria:
  - Technical quality and innovation
  - Potential impact
  - Code availability
  - Recentness
- **AI Summarization**: Generates technical summaries using Gemini Pro or Kimi AI
- **Paper Download**: Automatically downloads PDFs to organized folders
- **Google Drive Integration**: Automatically uploads results to Google Drive
- **Configurable**: Easily customizable search terms and ranking criteria
- **Scheduled Execution**: Can be set up to run automatically each week

## Prerequisites

- Python 3.7+
- Google AI Studio API key (for Gemini) or Kimi API key
- Internet connection

## Installation

1. Clone this repository or download the files
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Installation Verification

Run the provided test script to verify everything is working:
```bash
python test_installation.py
```

This will verify:
- Python version compatibility
- Required package installation
- Configuration file validity
- Script file presence

If all tests pass, you're ready to use the research agent!

## Configuration

The agent uses `config.json` for configuration:

- **research_settings**: Control research parameters
- **search_terms**: Customize search keywords
- **ranking_criteria**: Adjust ranking weights
- **ai_models**: Configure AI model settings

## Usage

### Basic Usage

```bash
# Run with default settings (7 days, 10 papers, Gemini)
python enhanced_ad_research_agent.py --api-key YOUR_API_KEY

# Run with custom parameters
python enhanced_ad_research_agent.py \
  --days 14 \
  --top 15 \
  --api-key YOUR_API_KEY \
  --model gemini
```

### Using Kimi AI

```bash
python enhanced_ad_research_agent.py \
  --api-key YOUR_KIMI_API_KEY \
  --model kimi
```

### API Key Format

For most systems, you can pass the API key directly:
```bash
python enhanced_ad_research_agent.py --api-key AIzaSyDz84i8o8dbXxBLZmoVTdhAu63GJt2o_lcY
```

On some systems with special characters in the API key, you might need to quote it:
```bash
python enhanced_ad_research_agent.py --api-key "AIzaSyDz84i8o8dbXxBLZmoVTdhAu63GJt2o_lcY"
```

### Command Line Arguments

- `--days`: Number of days to look back (default: 7)
- `--top`: Number of top papers to process (default: 10)
- `--api-key`: API key for the AI model
- `--model`: AI model to use (gemini or kimi)
- `--config`: Path to configuration file (default: config.json)

## Output

The agent creates a date-stamped folder (e.g., `ad_research_2025-08-02`) containing:

1. **Downloaded PDFs**: Top research papers
2. **research_results.json**: Structured data of all papers
3. **research_report.txt**: Human-readable report with summaries

## Google Drive Integration

The agent can automatically upload research results to Google Drive:

1. **Setup**: Follow the instructions in `GOOGLE_DRIVE_SETUP.md`
2. **Configuration**: Enable in `config.json`:
   ```json
   "upload_to_google_drive": true,
   "google_drive_folder_id": "YOUR_FOLDER_ID"
   ```
3. **First Run**: Authentication will open in your browser
4. **Subsequent Runs**: Uses saved credentials automatically

The results are uploaded as a zip file containing all research materials.

## Setting Up Automatic Weekly Execution

### Windows Task Scheduler

1. Create a batch file `run_research.bat`:
   ```batch
   @echo off
   cd /d "C:\path\to\your\research\agent"
   python enhanced_ad_research_agent.py --api-key YOUR_API_KEY
   ```

2. Open Task Scheduler and create a new task
3. Set trigger to weekly
4. Set action to run the batch file

### Linux/macOS Cron

Add to your crontab (`crontab -e`):
```bash
# Run every Monday at 9 AM
0 9 * * 1 /usr/bin/python3 /path/to/enhanced_ad_research_agent.py --api-key YOUR_API_KEY
```

## Customization

### Search Terms

Modify `search_terms` in `config.json` to focus on specific areas:
```json
"search_terms": [
    "BEV autonomous driving",
    "occupancy networks autonomous driving",
    "neural radiance fields autonomous driving",
    "multi-modal perception autonomous vehicles"
]
```

### Ranking Criteria

Adjust weights in `ranking_criteria`:
```json
"code_availability_bonus": 3.0,
"recency_bonus_max": 3.0
```

## API Keys

### Google AI Studio (Gemini)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Use with `--api-key YOUR_GOOGLE_AI_KEY`

### Kimi AI
1. Go to [Kimi API](https://platform.moonshot.cn/)
2. Create an API key
3. Use with `--api-key YOUR_KIMI_KEY --model kimi`

## Output Example

```
ad_research_2025-08-02/
├── research_results.json
├── research_report.txt
├── End-to-end Autonomous Driving via.pdf
├── BEV Perception for Autonomous Vehicles.pdf
├── ...
```

## Contributing

Feel free to submit issues and pull requests to improve the agent.

## License

This project is licensed under the MIT License.
