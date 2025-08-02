# Enhanced Automated Driving Research Agent

## Overview

The Enhanced Automated Driving Research Agent is an advanced AI-powered tool that automatically researches new papers and models in automated driving from the last 7 days. It now includes comprehensive YouTube video research capabilities in addition to academic paper analysis.

## Key Features

### 1. Multi-Source Research
- **Academic Papers**: Searches arXiv for the latest research papers
- **YouTube Videos**: Searches for relevant research videos, tutorials, and demonstrations

### 2. Intelligent Filtering
- Advanced filtering to exclude unrelated domains (medical, healthcare, underwater, etc.)
- Focus on autonomous driving, self-driving cars, and related technologies
- Duplicate detection and removal

### 3. AI-Powered Analysis
- **Paper Summarization**: Technical summaries using Google Gemini Pro or Kimi AI
- **Video Summarization**: Content analysis of YouTube videos
- **Ranking System**: Intelligent scoring based on quality, impact, and innovation

### 4. Comprehensive Ranking
- **Papers**: Ranked by technical quality, impact, innovation, code availability
- **Videos**: Ranked by tutorial quality, scientific value, practical value, views, likes

### 5. Rich Metadata Extraction
- **Papers**: Title, authors, abstract, publication date, PDF URL, citations
- **Videos**: Title, channel, description, publication date, duration, views, likes

### 6. Data Management
- Automatic downloading of papers (PDFs)
- Optional video downloading (requires pytubefix)
- JSON and human-readable text report generation
- Google Drive integration for result storage

## New YouTube Video Features

### Video Search Capabilities
- Searches YouTube for recent videos on autonomous driving research
- Filters by publication date (last 7 days by default)
- Excludes videos longer than configurable duration (default: 20 minutes)
- Applies same domain filtering as papers

### Video Analysis
- Extracts metadata: title, channel, description, views, likes
- Calculates publication date from relative timestamps ("2 days ago")
- Parses view counts with K/M/B suffix handling
- Analyzes video duration to filter out overly long content

### Video Ranking Criteria
- **Tutorial Quality**: Scores based on educational keywords
- **Scientific Value**: Scores based on research-related terms
- **Practical Value**: Scores based on demo/application keywords
- **Engagement**: Views and likes metrics
- **Recency**: Newer videos receive higher scores

### Video Summarization
- Technical summaries using the same AI models as papers
- Analysis of core concepts, novelty, and applications
- Extraction of code/paper/resource links mentioned
- Assessment of technical depth and quality

## Technical Implementation

### Data Classes
- `ResearchPaper`: Structured storage for paper metadata and analysis
- `ResearchVideo`: Structured storage for video metadata and analysis

### AI Model Support
- **Google Gemini Pro**: Primary model for summarization
- **Kimi AI**: Alternative model option
- **Fallback**: Basic template-based summaries

### Parallel Processing
- Concurrent processing of papers and videos
- Configurable worker threads (default: 3)
- Rate limiting for API calls

### Error Handling
- Robust error handling for network issues
- Graceful degradation when APIs are unavailable
- Comprehensive logging of processing steps

## Configuration Options

### Research Settings
- `days_back`: Time window for research (default: 7 days)
- `top_papers`: Number of papers to analyze (default: 10)
- `top_videos`: Number of videos to analyze (default: 5)
- `max_video_length_minutes`: Maximum video duration (default: 20)
- `parallel_workers`: Concurrent processing threads (default: 3)

### Search Terms
- Comprehensive list of autonomous driving related keywords
- Includes technical terms like "LiDAR", "sensor fusion", "BEV"
- Covers various aspects: perception, planning, control

### Exclusion Terms
- Filters out unrelated domains to maintain focus
- Medical, healthcare, underwater, and other non-AD topics

### Ranking Criteria
- Quality, impact, and innovation indicators
- Code availability bonuses
- Recency scoring adjustments

## Usage

### Command Line Interface
```bash
python enhanced_ad_research_agent.py --days 7 --top-papers 10 --top-videos 5 --model gemini --api-key YOUR_API_KEY
```

### Python API
```python
from enhanced_ad_research_agent import EnhancedADRResearchAgent

agent = EnhancedADRResearchAgent(api_key="YOUR_API_KEY", model="gemini")
results = agent.run_research(days_back=7, top_papers=10, top_videos=5)
```

## Output

### Generated Files
- `research_results.json`: Structured JSON data
- `research_report.txt`: Human-readable summary
- Downloaded PDF papers
- (Optional) Downloaded MP4 videos

### Report Structure
- Executive summary with key findings
- Ranked list of papers with technical summaries
- Ranked list of videos with content analysis
- Metadata for all analyzed items

## Dependencies

### Core Libraries
- `arxiv`: Academic paper searching
- `requests`: HTTP requests
- `google-generativeai`: Gemini API access
- `youtube-search-python`: YouTube video searching
- `pytubefix`: YouTube video downloading

### Google Integration
- `google-auth`: Authentication
- `google-auth-oauthlib`: OAuth flow
- `google-api-python-client`: Google Drive API

## Future Enhancements

### Planned Features
- Support for additional video platforms (Vimeo, conference recordings)
- Integration with academic databases (IEEE, Springer)
- Advanced citation analysis and impact scoring
- Multi-language support for international research
- Real-time notification system for breaking research
- Interactive dashboard for result visualization

### Technical Improvements
- Enhanced duplicate detection algorithms
- Improved metadata extraction accuracy
- Advanced natural language processing for content analysis
- Machine learning-based ranking optimization
- Distributed processing for large-scale research

## Conclusion

The Enhanced Automated Driving Research Agent represents a significant advancement in automated research tools for the autonomous driving domain. By combining academic paper analysis with YouTube video research, it provides a comprehensive view of the latest developments in the field, making it an invaluable tool for researchers, engineers, and technology enthusiasts working in autonomous driving.
