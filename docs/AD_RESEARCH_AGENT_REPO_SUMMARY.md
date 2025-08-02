# AD Research Agent Repository Summary

## Repository Structure

```
AD_research_agent/
├── .gitignore
├── config.json
├── enhanced_ad_research_agent.py
├── LICENSE
├── README.md
├── requirements.txt
├── run_research.bat
├── run_research.sh
├── test_installation.py
└── docs/
    ├── AD_RESEARCH_AGENT_SUMMARY.md
    ├── GOOGLE_DRIVE_FINAL_SETUP.md
    └── GOOGLE_DRIVE_SETUP.md
```

## Files Included

### Main Application Files
- **enhanced_ad_research_agent.py**: Main research agent with Google Drive integration
- **config.json**: Configuration file with search terms, ranking criteria, and settings
- **requirements.txt**: Python dependencies
- **README.md**: Project overview and usage instructions

### Documentation
- **docs/AD_RESEARCH_AGENT_SUMMARY.md**: Summary of the research agent features
- **docs/GOOGLE_DRIVE_SETUP.md**: Detailed Google Drive integration setup guide
- **docs/GOOGLE_DRIVE_FINAL_SETUP.md**: Final setup verification and next steps

### Scripts
- **run_research.bat**: Windows batch script to run the research agent
- **run_research.sh**: Linux/macOS shell script to run the research agent
- **test_installation.py**: Script to verify installation and dependencies

### Configuration
- **.gitignore**: Excludes confidential files, temporary files, and large binaries
- **LICENSE**: MIT License for the project

## Excluded Files (Confidential/Temporary)

The following files are excluded from the repository for security and size reasons:
- Google Drive credentials (`credentials.json`)
- Google Drive tokens (`token.json`)
- Large binary files (`.bin`, research results)
- Log files
- IDE configuration files
- OS-specific temporary files

## Features

1. **Automated Research**: Searches for recent papers in autonomous driving
2. **Intelligent Ranking**: Ranks papers based on quality, impact, innovation, and code availability
3. **AI Summarization**: Generates technical summaries using Google Gemini Pro or Kimi AI
4. **Paper Download**: Automatically downloads PDFs to organized folders
5. **Google Drive Integration**: Automatically uploads results to Google Drive
6. **Configurable**: Easily customizable search terms and ranking criteria
7. **Scheduled Execution**: Can be set up to run automatically each week

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default settings
python enhanced_ad_research_agent.py --api-key YOUR_API_KEY

# Run with custom parameters
python enhanced_ad_research_agent.py --days 14 --top 15 --api-key YOUR_API_KEY --model gemini
```

## Security

- All confidential files are excluded via `.gitignore`
- No API keys or credentials are included in the repository
- Authentication tokens are stored locally and never committed

## License

This project is licensed under the MIT License - see the LICENSE file for details.
