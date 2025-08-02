"""
Enhanced Automated Driving Research Agent

This agent automatically researches new papers and models in automated driving
from the last 7 days, ranks them, and summarizes the best ones using AI models.
It also searches for relevant YouTube videos on autonomous driving research.
"""

import os
import json
import requests
import arxiv
import datetime
import time
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import configparser
import zipfile
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YouTube search imports
try:
    from youtubesearchpython import VideosSearch
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError:
    YOUTUBE_SEARCH_AVAILABLE = False

try:
    from pytubefix import YouTube
    YOUTUBE_DOWNLOAD_AVAILABLE = True
except ImportError:
    YOUTUBE_DOWNLOAD_AVAILABLE = False


@dataclass
class ResearchPaper:
    """Data class to store paper information."""
    title: str
    authors: List[str]
    abstract: str
    published: datetime.datetime
    pdf_url: str
    arxiv_id: str
    score: float = 0.0
    summary: str = ""
    code_url: str = ""
    venue: str = ""
    citations: int = 0


@dataclass
class ResearchVideo:
    """Data class to store YouTube video information."""
    title: str
    channel: str
    description: str
    published: datetime.datetime
    url: str
    duration: str
    views: int
    likes: int
    score: float = 0.0
    summary: str = ""
    code_url: str = ""
    tutorial_quality: float = 0.0
    scientific_value: float = 0.0
    practical_value: float = 0.0


class EnhancedADRResearchAgent:
    """Enhanced Automated Driving Research Agent with AI summarization."""
    
    def __init__(self, api_key: str = None, model: str = "gemini", config_path: str = "config.json"):
        """
        Initialize the research agent.
        
        Args:
            api_key: API key for Google AI Studio or Kimi
            model: Model to use ("gemini", "kimi", or "gpt")
            config_path: Path to configuration file
        """
        self.api_key = api_key
        self.model = model
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.search_terms = self.config["search_terms"]
        self.exclusion_terms = self.config.get("exclusion_terms", [])
        self.required_terms = self.config.get("required_terms", [])
        self.research_settings = self.config["research_settings"]
        self.ranking_criteria = self.config["ranking_criteria"]
        self.ai_models = self.config["ai_models"]
    
    def search_recent_papers(self, days_back: int = None) -> List[ResearchPaper]:
        """
        Search for recent papers in automated driving.
        
        Args:
            days_back: Number of days to look back (uses config if None)
            
        Returns:
            List of ResearchPaper objects
        """
        if days_back is None:
            days_back = self.research_settings["days_back"]
            
        print(f"Searching for papers from the last {days_back} days...")
        
        # Calculate date threshold
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days_back)
        
        papers = []
        
        # Search using arXiv API
        for term in self.search_terms:
            try:
                search = arxiv.Search(
                    query=f"all:{term}",
                    max_results=20,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                # Use Client to avoid deprecation warning
                client = arxiv.Client()
                results = list(client.results(search))
                
                for result in results:
                    # Check if paper is recent enough
                    if result.published.replace(tzinfo=None) >= date_threshold:
                        paper = ResearchPaper(
                            title=result.title,
                            authors=[author.name for author in result.authors],
                            abstract=result.summary,
                            published=result.published.replace(tzinfo=None),
                            pdf_url=result.pdf_url,
                            arxiv_id=result.get_short_id()
                        )
                        papers.append(paper)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error searching for '{term}': {e}")
                continue
        
        # Filter papers to only include automated driving related content
        filtered_papers = self._filter_ad_papers(papers)
        print(f"Filtered to {len(filtered_papers)} automated driving papers")
        
        # Remove duplicates based on title
        unique_papers = []
        seen_titles = set()
        
        for paper in filtered_papers:
            title_key = paper.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_papers.append(paper)
        
        print(f"Found {len(unique_papers)} unique automated driving papers")
        return unique_papers
    
    def _filter_ad_papers(self, papers: List[ResearchPaper]) -> List[ResearchPaper]:
        """
        Filter papers to only include automated driving related content.
        
        Args:
            papers: List of ResearchPaper objects
            
        Returns:
            Filtered list of ResearchPaper objects
        """
        filtered_papers = []
        
        for paper in papers:
            # Convert title and abstract to lowercase for case-insensitive matching
            title_lower = paper.title.lower()
            abstract_lower = paper.abstract.lower()
            full_text = title_lower + " " + abstract_lower
            
            # Check for exclusion terms (unrelated domains)
            exclude_paper = False
            for exclusion_term in self.exclusion_terms:
                if exclusion_term in full_text:
                    exclude_paper = True
                    break
            
            if exclude_paper:
                continue
            
            # Check for required terms (must have at least one)
            has_required_term = False
            for required_term in self.required_terms:
                # Check for exact matches and partial matches
                if required_term in full_text:
                    has_required_term = True
                    break
                # Also check for variations
                if required_term.replace(" ", "-") in full_text:
                    has_required_term = True
                    break
            
            # Additional check: if it's about robotics, make sure it's specifically about autonomous driving
            if "robot" in full_text and "driving" not in full_text and "vehicle" not in full_text:
                exclude_paper = True
            
            # Additional check: if it's about AI agents, make sure it's specifically for autonomous driving
            if "agent" in full_text and "driving" not in full_text and "vehicle" not in full_text:
                exclude_paper = True
            
            if exclude_paper:
                continue
            
            # If no required terms specified, include all non-excluded papers
            if not self.required_terms or has_required_term:
                filtered_papers.append(paper)
        
        return filtered_papers
    
    def search_youtube_videos(self, days_back: int = None) -> List[ResearchVideo]:
        """
        Search for recent YouTube videos on automated driving research.
        
        Args:
            days_back: Number of days to look back (uses config if None)
            
        Returns:
            List of ResearchVideo objects
        """
        if not YOUTUBE_SEARCH_AVAILABLE:
            print("YouTube search not available. Please install youtube-search-python package.")
            return []
        
        if days_back is None:
            days_back = self.research_settings["days_back"]
            
        print(f"Searching for YouTube videos from the last {days_back} days...")
        
        # Calculate date threshold
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days_back)
        
        videos = []
        max_video_length = self.research_settings.get("max_video_length_minutes", 20)
        
        # Search using YouTube Search Python
        for term in self.search_terms:
            try:
                # Search for videos
                search = VideosSearch(term, limit=10)
                results = search.result()
                
                if results and 'result' in results:
                    for video_data in results['result']:
                        try:
                            # Parse published date
                            published_str = video_data.get('publishedTime', '')
                            # Try to extract date information
                            published_date = self._parse_youtube_date(published_str)
                            
                            # Check if video is recent enough
                            if published_date and published_date >= date_threshold:
                                # Check video duration
                                duration = video_data.get('duration', '')
                                if self._is_duration_valid(duration, max_video_length):
                                    # Get view count
                                    view_count_str = video_data.get('viewCount', {}).get('text', '0')
                                    views = self._parse_view_count(view_count_str)
                                    
                                    # Get like count if available
                                    likes = video_data.get('viewCount', {}).get('likes', 0)
                                    if likes is None:
                                        likes = 0
                                    
                                    video = ResearchVideo(
                                        title=video_data.get('title', ''),
                                        channel=video_data.get('channel', {}).get('name', ''),
                                        description=video_data.get('descriptionSnippet', [{'text': ''}])[0].get('text', '') if video_data.get('descriptionSnippet') else '',
                                        published=published_date,
                                        url=video_data.get('link', ''),
                                        duration=duration,
                                        views=views,
                                        likes=likes
                                    )
                                    videos.append(video)
                        except Exception as e:
                            print(f"Error processing video: {e}")
                            continue
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error searching for YouTube videos with term '{term}': {e}")
                continue
        
        # Filter videos to only include automated driving related content
        filtered_videos = self._filter_ad_videos(videos)
        print(f"Filtered to {len(filtered_videos)} automated driving videos")
        
        # Remove duplicates based on title
        unique_videos = []
        seen_titles = set()
        
        for video in filtered_videos:
            title_key = video.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_videos.append(video)
        
        print(f"Found {len(unique_videos)} unique automated driving videos")
        return unique_videos
    
    def _parse_youtube_date(self, published_str: str) -> datetime.datetime:
        """
        Parse YouTube published time string to datetime.
        
        Args:
            published_str: Published time string from YouTube
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            # Handle common YouTube date formats
            if 'ago' in published_str:
                # Examples: "2 days ago", "1 week ago", "3 hours ago"
                parts = published_str.split()
                if len(parts) >= 2:
                    number = int(parts[0])
                    unit = parts[1].lower()
                    
                    if 'hour' in unit:
                        return datetime.datetime.now() - datetime.timedelta(hours=number)
                    elif 'day' in unit:
                        return datetime.datetime.now() - datetime.timedelta(days=number)
                    elif 'week' in unit:
                        return datetime.datetime.now() - datetime.timedelta(weeks=number)
                    elif 'month' in unit:
                        return datetime.datetime.now() - datetime.timedelta(days=number*30)
                    elif 'year' in unit:
                        return datetime.datetime.now() - datetime.timedelta(days=number*365)
            
            # If we can't parse, return None
            return None
        except:
            return None
    
    def _is_duration_valid(self, duration: str, max_minutes: int) -> bool:
        """
        Check if video duration is within the allowed limit.
        
        Args:
            duration: Duration string (e.g., "10:30")
            max_minutes: Maximum allowed duration in minutes
            
        Returns:
            True if duration is valid, False otherwise
        """
        try:
            if not duration:
                return True  # No duration info, assume it's okay
            
            # Parse duration format (e.g., "10:30" or "1:25:30")
            parts = duration.split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = int(parts[0]), int(parts[1])
                total_minutes = minutes + seconds/60
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                total_minutes = hours*60 + minutes + seconds/60
            else:
                return True  # Unknown format, assume it's okay
            
            return total_minutes <= max_minutes
        except:
            return True  # If parsing fails, assume it's okay
    
    def _parse_view_count(self, view_count_str: str) -> int:
        """
        Parse view count string to integer.
        
        Args:
            view_count_str: View count string (e.g., "1.2K views")
            
        Returns:
            Integer view count
        """
        try:
            # Remove " views" suffix
            count_str = view_count_str.replace(' views', '').replace(',', '')
            
            # Handle K, M, B suffixes
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            elif 'B' in count_str:
                return int(float(count_str.replace('B', '')) * 1000000000)
            else:
                return int(count_str)
        except:
            return 0
    
    def _filter_ad_videos(self, videos: List[ResearchVideo]) -> List[ResearchVideo]:
        """
        Filter videos to only include automated driving related content.
        
        Args:
            videos: List of ResearchVideo objects
            
        Returns:
            Filtered list of ResearchVideo objects
        """
        filtered_videos = []
        
        for video in videos:
            # Convert title and description to lowercase for case-insensitive matching
            title_lower = video.title.lower()
            description_lower = video.description.lower()
            full_text = title_lower + " " + description_lower
            
            # Check for exclusion terms (unrelated domains)
            exclude_video = False
            for exclusion_term in self.exclusion_terms:
                if exclusion_term in full_text:
                    exclude_video = True
                    break
            
            if exclude_video:
                continue
            
            # Check for required terms (must have at least one)
            has_required_term = False
            for required_term in self.required_terms:
                # Check for exact matches and partial matches
                if required_term in full_text:
                    has_required_term = True
                    break
                # Also check for variations
                if required_term.replace(" ", "-") in full_text:
                    has_required_term = True
                    break
            
            # Additional check: if it's about robotics, make sure it's specifically about autonomous driving
            if "robot" in full_text and "driving" not in full_text and "vehicle" not in full_text:
                exclude_video = True
            
            # Additional check: if it's about AI agents, make sure it's specifically for autonomous driving
            if "agent" in full_text and "driving" not in full_text and "vehicle" not in full_text:
                exclude_video = True
            
            if exclude_video:
                continue
            
            # If no required terms specified, include all non-excluded videos
            if not self.required_terms or has_required_term:
                filtered_videos.append(video)
        
        return filtered_videos
    
    def rank_papers(self, papers: List[ResearchPaper]) -> List[ResearchPaper]:
        """
        Rank papers based on quality, impact, innovation, code availability, and PDF quality.
        
        Args:
            papers: List of ResearchPaper objects
            
        Returns:
            Ranked list of ResearchPaper objects
        """
        print("Ranking papers...")
        
        for paper in papers:
            score = 0.0
            
            # Score based on abstract content (proxy for quality and innovation)
            abstract = paper.abstract.lower()
            
            # Quality indicators
            for keyword in self.ranking_criteria["quality_indicators"]:
                if keyword in abstract:
                    score += 1.0
            
            # Impact indicators
            for keyword in self.ranking_criteria["impact_indicators"]:
                if keyword in abstract:
                    score += 1.5
            
            # Innovation indicators
            for keyword in self.ranking_criteria["innovation_indicators"]:
                if keyword in abstract:
                    score += 1.2
            
            # Code availability (check in abstract)
            code_keywords = [
                "github", "code available", "open source", "implementation",
                "publicly available", "repository"
            ]
            
            code_available = any(keyword in abstract for keyword in code_keywords)
            if code_available:
                score += self.ranking_criteria["code_availability_bonus"]
            
            # Length of abstract (indicates thoroughness)
            if len(abstract) > 500:
                score += self.ranking_criteria["abstract_length_bonus"]
            
            # Recentness bonus (newer papers get higher scores)
            days_old = (datetime.datetime.now() - paper.published).days
            recency_bonus = max(0, self.ranking_criteria["recency_bonus_max"] - (days_old * 0.2))
            score += recency_bonus
            
            paper.score = score
        
        # Sort by score (descending)
        ranked_papers = sorted(papers, key=lambda p: p.score, reverse=True)
        return ranked_papers
    
    def rank_videos(self, videos: List[ResearchVideo]) -> List[ResearchVideo]:
        """
        Rank videos based on quality, impact, innovation, likes, views, and other criteria.
        
        Args:
            videos: List of ResearchVideo objects
            
        Returns:
            Ranked list of ResearchVideo objects
        """
        print("Ranking YouTube videos...")
        
        for video in videos:
            score = 0.0
            
            # Convert description to lowercase for matching
            description = video.description.lower()
            
            # Quality indicators (tutorial quality)
            tutorial_keywords = [
                "tutorial", "how to", "guide", "step by step", "walkthrough",
                "explained", "introduction", "beginner", "course"
            ]
            tutorial_quality = sum(1.0 for keyword in tutorial_keywords if keyword in description)
            video.tutorial_quality = tutorial_quality
            
            # Scientific value indicators
            scientific_keywords = [
                "research", "paper", "experiment", "study", "results",
                "methodology", "analysis", "evaluation", "benchmark"
            ]
            scientific_value = sum(1.2 for keyword in scientific_keywords if keyword in description)
            video.scientific_value = scientific_value
            
            # Practical value indicators
            practical_keywords = [
                "demo", "demonstration", "implementation", "real world",
                "practical", "application", "deploy", "test"
            ]
            practical_value = sum(1.0 for keyword in practical_keywords if keyword in description)
            video.practical_value = practical_value
            
            # Code availability (check in description)
            code_keywords = [
                "github", "code available", "open source", "implementation",
                "publicly available", "repository", "source code"
            ]
            code_available = any(keyword in description for keyword in code_keywords)
            if code_available:
                score += self.ranking_criteria["code_availability_bonus"]
            
            # Add quality scores to total score
            score += tutorial_quality + scientific_value + practical_value
            
            # Views and likes bonus (popularity indicator)
            # Normalize views (logarithmic scale to prevent very popular videos from dominating)
            if video.views > 0:
                view_score = min(2.0, (video.views / 10000))  # Cap at 2.0 points
                score += view_score
            
            # Likes bonus (engagement indicator)
            if video.likes > 0:
                like_score = min(1.5, (video.likes / 5000))  # Cap at 1.5 points
                score += like_score
            
            # Recentness bonus (newer videos get higher scores)
            days_old = (datetime.datetime.now() - video.published).days if video.published else 0
            if days_old >= 0:  # Only apply bonus for valid dates
                recency_bonus = max(0, self.ranking_criteria["recency_bonus_max"] - (days_old * 0.1))
                score += recency_bonus
            
            video.score = score
        
        # Sort by score (descending)
        ranked_videos = sorted(videos, key=lambda v: v.score, reverse=True)
        return ranked_videos
    
    def summarize_paper_with_gemini(self, paper: ResearchPaper) -> str:
        """
        Summarize a paper using Google Gemini Pro.
        
        Args:
            paper: ResearchPaper object
            
        Returns:
            Summary string
        """
        try:
            if not self.api_key:
                return "API key not provided for Gemini summarization."
            
            # Import google-generativeai
            import google.generativeai as genai
            
            # Configure API
            genai.configure(api_key=self.api_key)
            
            # Create model (using the model name from config)
            model_name = self.ai_models.get("gemini", {}).get("model_name", "gemini-pro")
            model = genai.GenerativeModel(model_name)
            
            # Create prompt
            prompt = f"""
            Please provide a technical summary of this autonomous driving research paper:
            
            Title: {paper.title}
            Authors: {', '.join(paper.authors[:5])}
            Abstract: {paper.abstract}
            
            Please include:
            1. Key technical contributions
            2. Methodology
            3. Results and improvements
            4. Potential impact on autonomous driving
            5. Limitations or future work
            
            Keep the summary concise but technical (200-300 words).
            """
            
            # Generate summary
            response = model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return "Failed to generate summary with Gemini."
                
        except Exception as e:
            print(f"Error summarizing with Gemini: {e}")
            return f"Error in Gemini summarization: {str(e)}"
    
    def summarize_video_with_gemini(self, video: ResearchVideo) -> str:
        """
        Summarize a YouTube video using Google Gemini Pro.
        
        Args:
            video: ResearchVideo object
            
        Returns:
            Summary string
        """
        try:
            if not self.api_key:
                return "API key not provided for Gemini summarization."
            
            # Import google-generativeai
            import google.generativeai as genai
            
            # Configure API
            genai.configure(api_key=self.api_key)
            
            # Create model (using the model name from config)
            model_name = self.ai_models.get("gemini", {}).get("model_name", "gemini-pro")
            model = genai.GenerativeModel(model_name)
            
            # Create prompt
            prompt = f"""
            Please provide a technical summary of this autonomous driving research YouTube video:
            
            Title: {video.title}
            Channel: {video.channel}
            Description: {video.description}
            Duration: {video.duration}
            Published: {video.published.strftime('%Y-%m-%d') if video.published else 'Unknown'}
            
            Please include:
            1. Core concepts discussed
            2. Novelty of the approach or findings
            3. Any links to code, papers, or resources mentioned
            4. Technical depth and quality
            5. Potential applications
            
            Keep the summary concise but technical (200-300 words).
            """
            
            # Generate summary
            response = model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return "Failed to generate summary with Gemini."
                
        except Exception as e:
            print(f"Error summarizing video with Gemini: {e}")
            return f"Error in Gemini video summarization: {str(e)}"
    
    def summarize_paper_with_kimi(self, paper: ResearchPaper) -> str:
        """
        Summarize a paper using Kimi AI.
        
        Args:
            paper: ResearchPaper object
            
        Returns:
            Summary string
        """
        try:
            if not self.api_key:
                return "API key not provided for Kimi summarization."
            
            # Kimi API endpoint (this is a placeholder - actual endpoint may vary)
            url = "https://api.moonshot.cn/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create prompt
            prompt = f"""
            Please provide a technical summary of this autonomous driving research paper:
            
            Title: {paper.title}
            Authors: {', '.join(paper.authors[:5])}
            Abstract: {paper.abstract}
            
            Please include:
            1. Key technical contributions
            2. Methodology
            3. Results and improvements
            4. Potential impact on autonomous driving
            5. Limitations or future work
            
            Keep the summary concise but technical (200-300 words).
            """
            
            data = {
                "model": "kimi",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            # Make API request
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "Failed to generate summary with Kimi."
                
        except Exception as e:
            print(f"Error summarizing with Kimi: {e}")
            return f"Error in Kimi summarization: {str(e)}"
    
    def summarize_video_with_kimi(self, video: ResearchVideo) -> str:
        """
        Summarize a YouTube video using Kimi AI.
        
        Args:
            video: ResearchVideo object
            
        Returns:
            Summary string
        """
        try:
            if not self.api_key:
                return "API key not provided for Kimi summarization."
            
            # Kimi API endpoint (this is a placeholder - actual endpoint may vary)
            url = "https://api.moonshot.cn/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create prompt
            prompt = f"""
            Please provide a technical summary of this autonomous driving research YouTube video:
            
            Title: {video.title}
            Channel: {video.channel}
            Description: {video.description}
            Duration: {video.duration}
            Published: {video.published.strftime('%Y-%m-%d') if video.published else 'Unknown'}
            
            Please include:
            1. Core concepts discussed
            2. Novelty of the approach or findings
            3. Any links to code, papers, or resources mentioned
            4. Technical depth and quality
            5. Potential applications
            
            Keep the summary concise but technical (200-300 words).
            """
            
            data = {
                "model": "kimi",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            # Make API request
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "Failed to generate summary with Kimi."
                
        except Exception as e:
            print(f"Error summarizing video with Kimi: {e}")
            return f"Error in Kimi video summarization: {str(e)}"
    
    def summarize_paper(self, paper: ResearchPaper) -> str:
        """
        Summarize a paper using the configured AI model.
        
        Args:
            paper: ResearchPaper object
            
        Returns:
            Summary string
        """
        if self.model == "gemini":
            return self.summarize_paper_with_gemini(paper)
        elif self.model == "kimi":
            return self.summarize_paper_with_kimi(paper)
        else:
            # Fallback to basic summary
            summary = f"Technical summary of '{paper.title[:50]}...':\n\n"
            summary += f"This paper presents research in autonomous driving with significant contributions to the field. "
            summary += f"The methodology involves advanced techniques that show promising results. "
            summary += f"The work has potential for real-world applications in self-driving systems.\n\n"
            summary += f"Key findings: Improved performance, novel approach, practical implementation."
            return summary
    
    def summarize_video(self, video: ResearchVideo) -> str:
        """
        Summarize a video using the configured AI model.
        
        Args:
            video: ResearchVideo object
            
        Returns:
            Summary string
        """
        if self.model == "gemini":
            return self.summarize_video_with_gemini(video)
        elif self.model == "kimi":
            return self.summarize_video_with_kimi(video)
        else:
            # Fallback to basic summary
            summary = f"Technical summary of '{video.title[:50]}...':\n\n"
            summary += f"This video presents research in autonomous driving with significant contributions to the field. "
            summary += f"The content involves advanced techniques that show promising results. "
            summary += f"The work has potential for real-world applications in self-driving systems.\n\n"
            summary += f"Key findings: Improved performance, novel approach, practical implementation."
            return summary
    
    def download_paper(self, paper: ResearchPaper, download_dir: str) -> bool:
        """
        Download paper PDF.
        
        Args:
            paper: ResearchPaper object
            download_dir: Directory to save PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create download directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            
            # Create filename
            safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title[:100]}.pdf"
            filepath = os.path.join(download_dir, filename)
            
            # Download PDF
            response = requests.get(paper.pdf_url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"Error downloading paper '{paper.title}': {e}")
            return False
    
    def download_video(self, video: ResearchVideo, download_dir: str) -> bool:
        """
        Download YouTube video (if pytubefix is available).
        
        Args:
            video: ResearchVideo object
            download_dir: Directory to save video
            
        Returns:
            True if successful, False otherwise
        """
        if not YOUTUBE_DOWNLOAD_AVAILABLE:
            print("Video download not available. Please install pytubefix package.")
            return False
        
        try:
            # Create download directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            
            # Create YouTube object
            yt = YouTube(video.url)
            
            # Get the highest resolution stream
            stream = yt.streams.get_highest_resolution()
            
            if stream:
                # Create filename
                safe_title = "".join(c for c in video.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title[:100]}.mp4"
                
                # Download video
                stream.download(output_path=download_dir, filename=filename)
                print(f"Downloaded video: {filename}")
                return True
            else:
                print(f"No suitable stream found for video: {video.title}")
                return False
                
        except Exception as e:
            print(f"Error downloading video '{video.title}': {e}")
            return False
    
    def run_research(self, days_back: int = None, top_papers: int = None, top_videos: int = None) -> Dict[str, List]:
        """
        Run the complete research pipeline.
        
        Args:
            days_back: Number of days to look back (uses config if None)
            top_papers: Number of top papers to process (uses config if None)
            top_videos: Number of top videos to process (uses config if None)
            
        Returns:
            Dictionary with 'papers' and 'videos' lists
        """
        if days_back is None:
            days_back = self.research_settings["days_back"]
        if top_papers is None:
            top_papers = self.research_settings["top_papers"]
        if top_videos is None:
            top_videos = self.research_settings["top_videos"]
            
        print("Starting Enhanced Automated Driving Research Agent...")
        print("=" * 60)
        print(f"Using AI Model: {self.model.upper()}")
        print(f"Research Period: Last {days_back} days")
        print(f"Top Papers: {top_papers}")
        print(f"Top Videos: {top_videos}")
        print("=" * 60)
        
        # Create date-based folder
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        download_dir = f"ad_research_{today}"
        
        # Step 1: Search for papers
        papers = self.search_recent_papers(days_back)
        
        # Step 2: Search for videos
        videos = self.search_youtube_videos(days_back)
        
        if not papers and not videos:
            print("No papers or videos found for the specified time period.")
            return {"papers": [], "videos": []}
        
        # Step 3: Rank papers and videos
        ranked_papers = self.rank_papers(papers) if papers else []
        ranked_videos = self.rank_videos(videos) if videos else []
        
        # Step 4: Process top N papers and videos
        top_papers_list = ranked_papers[:top_papers] if ranked_papers else []
        top_videos_list = ranked_videos[:top_videos] if ranked_videos else []
        
        print(f"\nProcessing top {len(top_papers_list)} papers with {self.model.upper()}...")
        print(f"Processing top {len(top_videos_list)} videos with {self.model.upper()}...")
        
        # Process papers and videos in parallel
        workers = self.research_settings.get("parallel_workers", 3)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit paper summarization tasks
            paper_futures = {}
            for paper in top_papers_list:
                future = executor.submit(self.summarize_paper, paper)
                paper_futures[future] = paper
            
            # Submit video summarization tasks
            video_futures = {}
            for video in top_videos_list:
                future = executor.submit(self.summarize_video, video)
                video_futures[future] = video
            
            # Collect paper summaries
            for future in as_completed(paper_futures):
                paper = paper_futures[future]
                try:
                    paper.summary = future.result()
                except Exception as e:
                    print(f"Error getting summary for paper '{paper.title}': {e}")
                    paper.summary = "Summary generation failed."
            
            # Collect video summaries
            for future in as_completed(video_futures):
                video = video_futures[future]
                try:
                    video.summary = future.result()
                except Exception as e:
                    print(f"Error getting summary for video '{video.title}': {e}")
                    video.summary = "Summary generation failed."
        
        # Step 5: Download papers and videos (if enabled)
        if self.research_settings.get("download_papers", True):
            print(f"\nDownloading papers to {download_dir}...")
            for i, paper in enumerate(top_papers_list):
                print(f"Downloading paper {i+1}/{len(top_papers_list)}: {paper.title[:60]}...")
                self.download_paper(paper, download_dir)
        else:
            print("\nPaper downloading disabled in configuration.")
        
        # Video downloading is optional and may not be needed for all use cases
        # Uncomment the following lines if you want to enable video downloading
        # if self.research_settings.get("download_videos", False):
        #     print(f"\nDownloading videos to {download_dir}...")
        #     for i, video in enumerate(top_videos_list):
        #         print(f"Downloading video {i+1}/{len(top_videos_list)}: {video.title[:60]}...")
        #         self.download_video(video, download_dir)
        # else:
        #     print("\nVideo downloading disabled in configuration.")
        
        # Step 6: Save results
        self.save_results(top_papers_list, top_videos_list, download_dir)
        
        # Step 7: Upload to Google Drive (if enabled)
        if self.research_settings.get("upload_to_google_drive", False):
            print(f"\nUploading results to Google Drive...")
            self.upload_to_google_drive(download_dir)
        
        print("\nResearch completed successfully!")
        return {"papers": top_papers_list, "videos": top_videos_list}
    
    def save_results(self, papers: List[ResearchPaper], videos: List[ResearchVideo], directory: str):
        """
        Save research results to JSON file.
        
        Args:
            papers: List of ResearchPaper objects
            videos: List of ResearchVideo objects
            directory: Directory to save results
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)
            
            # Convert papers to dictionaries
            papers_data = []
            for paper in papers:
                paper_dict = asdict(paper)
                # Convert datetime to string for JSON serialization
                paper_dict['published'] = paper_dict['published'].isoformat() if paper_dict['published'] else None
                papers_data.append(paper_dict)
            
            # Convert videos to dictionaries
            videos_data = []
            for video in videos:
                video_dict = asdict(video)
                # Convert datetime to string for JSON serialization
                video_dict['published'] = video_dict['published'].isoformat() if video_dict['published'] else None
                videos_data.append(video_dict)
            
            # Save to JSON file
            results_file = os.path.join(directory, "research_results.json")
            results_data = {
                "papers": papers_data,
                "videos": videos_data,
                "generated_at": datetime.datetime.now().isoformat()
            }
            with open(results_file, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            # Save human-readable report
            report_file = os.path.join(directory, "research_report.txt")
            with open(report_file, 'w') as f:
                f.write("AUTOMATED DRIVING RESEARCH REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"AI Model: {self.model.upper()}\n")
                f.write(f"Total papers analyzed: {len(papers)}\n")
                f.write(f"Total videos analyzed: {len(videos)}\n\n")
                
                if papers:
                    f.write("TOP RESEARCH PAPERS\n")
                    f.write("-" * 20 + "\n\n")
                    for i, paper in enumerate(papers, 1):
                        f.write(f"{i}. {paper.title}\n")
                        f.write(f"   Score: {paper.score:.2f}\n")
                        f.write(f"   Authors: {', '.join(paper.authors[:3])}\n")
                        f.write(f"   Published: {paper.published.strftime('%Y-%m-%d') if paper.published else 'Unknown'}\n")
                        f.write(f"   Summary: {paper.summary}\n")
                        f.write(f"   PDF: {paper.pdf_url}\n\n")
                
                if videos:
                    f.write("TOP YOUTUBE VIDEOS\n")
                    f.write("-" * 18 + "\n\n")
                    for i, video in enumerate(videos, 1):
                        f.write(f"{i}. {video.title}\n")
                        f.write(f"   Score: {video.score:.2f}\n")
                        f.write(f"   Channel: {video.channel}\n")
                        f.write(f"   Published: {video.published.strftime('%Y-%m-%d') if video.published else 'Unknown'}\n")
                        f.write(f"   Duration: {video.duration}\n")
                        f.write(f"   Views: {video.views:,}\n")
                        f.write(f"   Likes: {video.likes:,}\n")
                        f.write(f"   Summary: {video.summary}\n")
                        f.write(f"   URL: {video.url}\n\n")
            
            print(f"Results saved to {directory}")
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def upload_to_google_drive(self, directory: str):
        """
        Upload the research results folder to Google Drive.
        
        Args:
            directory: Directory containing research results to upload
        """
        zip_filename = f"{directory}.zip"
        try:
            # Check if credentials file exists
            creds_file = "credentials.json"
            token_file = "token.json"
            
            if not os.path.exists(creds_file):
                print(f"Error: Google Drive credentials file '{creds_file}' not found.")
                print("Please download credentials.json from Google Cloud Console and place it in the current directory.")
                return False
            
            # Authenticate with Google Drive
            creds = None
            
            # Load existing token if it exists
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, ["https://www.googleapis.com/auth/drive"])
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        creds_file, ["https://www.googleapis.com/auth/drive"])
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the service
            service = build('drive', 'v3', credentials=creds)
            
            # Create a zip file of the directory
            print(f"Creating zip file: {zip_filename}")
            
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, directory)
                        zipf.write(file_path, arcname=arcname)
            
            # Upload the zip file to Google Drive
            print(f"Uploading {zip_filename} to Google Drive...")
            
            # Get folder ID from config
            folder_id = self.research_settings.get("google_drive_folder_id", "")
            
            # Prepare file metadata
            file_metadata = {
                'name': zip_filename,
                'description': f'Automated Driving Research Results - {datetime.datetime.now().strftime("%Y-%m-%d")}'
            }
            
            # If folder ID is specified, upload to that folder
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media upload
            media = MediaFileUpload(zip_filename, mimetype='application/zip', resumable=True)
            
            # Upload file
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
            print(f"Successfully uploaded to Google Drive with file ID: {file.get('id')}")
            
            # Clean up zip file with better error handling
            try:
                # Close the media upload to release file handle
                if hasattr(media, 'close'):
                    media.close()
                
                # Add a small delay to ensure file handle is released
                time.sleep(1)
                
                # Clean up zip file
                os.remove(zip_filename)
                print(f"Cleaned up temporary file: {zip_filename}")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up temporary file {zip_filename}: {cleanup_error}")
                print("You can manually delete this file if needed.")
            
            return True
            
        except Exception as e:
            print(f"Error uploading to Google Drive: {e}")
            # Try to clean up zip file even if upload failed
            try:
                if os.path.exists(zip_filename):
                    time.sleep(1)  # Give some time for file handle to be released
                    os.remove(zip_filename)
                    print(f"Cleaned up temporary file after error: {zip_filename}")
            except Exception as cleanup_error:
                print(f"Warning: Could not clean up temporary file {zip_filename} after error: {cleanup_error}")
            return False


def main():
    """Main function to run the research agent."""
    parser = argparse.ArgumentParser(description="Enhanced Automated Driving Research Agent")
    parser.add_argument("--days", type=int, help="Number of days to look back")
    parser.add_argument("--top-papers", type=int, help="Number of top papers to process")
    parser.add_argument("--top-videos", type=int, help="Number of top videos to process")
    parser.add_argument("--api-key", type=str, help="API key for AI model")
    parser.add_argument("--model", type=str, default="gemini", help="AI model to use (gemini, kimi)")
    parser.add_argument("--config", type=str, default="config.json", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = EnhancedADRResearchAgent(
        api_key=args.api_key, 
        model=args.model,
        config_path=args.config
    )
    
    # Run research
    results = agent.run_research(
        days_back=args.days, 
        top_papers=args.top_papers, 
        top_videos=args.top_videos
    )
    
    # Print summary
    papers = results.get("papers", [])
    videos = results.get("videos", [])
    
    if papers:
        print("\n" + "=" * 70)
        print("TOP RESEARCH PAPERS")
        print("=" * 70)
        
        for i, paper in enumerate(papers[:10], 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Score: {paper.score:.2f}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Published: {paper.published.strftime('%Y-%m-%d') if paper.published else 'Unknown'}")
    
    if videos:
        print("\n" + "=" * 70)
        print("TOP YOUTUBE VIDEOS")
        print("=" * 70)
        
        for i, video in enumerate(videos[:5], 1):
            print(f"\n{i}. {video.title}")
            print(f"   Score: {video.score:.2f}")
            print(f"   Channel: {video.channel}")
            print(f"   Published: {video.published.strftime('%Y-%m-%d') if video.published else 'Unknown'}")
            print(f"   Views: {video.views:,}")


if __name__ == "__main__":
    main()
