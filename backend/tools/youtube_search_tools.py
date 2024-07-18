from typing import List, Type
from pydantic.v1 import BaseModel, Field
import os
import requests
from crewai_tools import BaseTool
from dotenv import load_dotenv

load_dotenv()


class VideoSearchResult(BaseModel):
    title: str
    video_url: str


class YoutubeVideoSearchToolInput(BaseModel):
    keyword: str = Field(..., description="The search keyword")
    max_result: int = Field(
        10, description="The maximum number of result to return")


class YoutubeVideoSearchTool(BaseModel):
    name: str = "Search Youtube Videos"
    description: str = "Searches Youtube videos based on a keyword and returns a list of video search results."
    args_schema: Type[BaseModel] = YoutubeVideoSearchToolInput

    def _run(self, keyword: str, max_results: int = 10) -> List[VideoSearchResult]:
        api_key = os.getenv("YOUTUBE_API_KEY")
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": keyword,
            "maxResults": max_results,
            "type": "video",
            "key": api_key
        }
        response = requests.get(url, params)
        response.raise_for_status()
        items = response.json().get("items", [])

        results = []
        for item in items:
            title = item["snippet"]["title"]
            video_id = item["id"]["video"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            results.append(VideoSearchResult(
                title=title, video_url=video_url,))

        return results
