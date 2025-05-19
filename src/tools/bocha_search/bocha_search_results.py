import json
from typing import Dict, List, Optional, Tuple, Union

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import Field

from src.tools.bocha_search.bocha_search_api_wrapper import BochaSearchAPIWrapper


class BochaSearchResultsWithImages(BaseTool):
    """Tool that queries the Web Search API and gets back detailed web search results.
    
    This tool performs web searches using the Web Search API, providing high-quality
    search results including web pages, snippets, summaries, and optionally images.
    
    Input: A search query string (e.g., "阿里巴巴2024年ESG报告")
    
    Output: A list of search results containing:
    - Page title
    - URL
    - Content summary/snippet
    - Site name
    - Site icon
    - Publication date
    - Images (if enabled)
    """

    name: str = "bocha_search"
    description: str = (
        "A powerful web search tool...\n\n"
        "To use this tool, provide a search query in one of these formats:\n"
        "1. web_search(query=\"your search term\")\n"
        "2. web_search(\"your search term\")\n"
        "Example: web_search(\"2024 Olympic medal count\")"
    )

    count: int = 10
    """Number of results to return. Range: 1-50. Default is 10."""

    freshness: str = "noLimit"
    """Time range for search results. Default is 'noLimit'.
    Options:
    - 'oneDay': Search results from the past day
    - 'oneWeek': Search results from the past week
    - 'oneMonth': Search results from the past month
    - 'oneYear': Search results from the past year
    - 'noLimit': No time limitation (default)
    - 'YYYY-MM-DD..YYYY-MM-DD': Custom date range, e.g. '2023-01-01..2023-12-31'
    - 'YYYY-MM-DD': Search for a specific date, e.g. '2023-12-31'
    """

    summary: bool = True
    """Include detailed text summaries in the response. 
    - True: Return detailed summaries (default)
    - False: Return only short snippets
    """
    
    include: Optional[List[str]] = None
    """List of domains to include in search results.
    Format: ['example.com', 'example.org']
    
    Can include up to 20 domains separated by '|' or ','
    Example: ['qq.com', 'm.163.com']
    """
    
    exclude: Optional[List[str]] = None
    """List of domains to exclude from search results.
    Format: ['example.com', 'example.org']
    
    Can include up to 20 domains separated by '|' or ','
    Example: ['qq.com', 'm.163.com']
    """

    include_images: bool = True
    """Include images in the search results.
    - True: Return image results along with web pages (default)
    - False: Return only web page results
    """
    
    api_wrapper: BochaSearchAPIWrapper = Field(default_factory=BochaSearchAPIWrapper)

    def _run(
        self,
        query: str = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs
    ) -> Union[List[Dict[str, str]], str]:
        """Execute the web search synchronously.
        
        Args:
            query: The search query string, or can be passed as kwargs["args"]["query"]
            run_manager: Optional callback manager
            
        Returns:
            List of cleaned search results with page information and optional images
        """
        # Handle both direct query string and args format
        if query is None and "args" in kwargs:
            args = kwargs["args"]
            if isinstance(args, dict) and "query" in args:
                query = args["query"]
            elif isinstance(args, str):
                query = args
            elif isinstance(args, list) and len(args) > 0:
                # Handle list format - use the first item as the query
                query = args[0]
                
        if not query:
            return "Error: No search query provided"
            
        try:
            raw_results = self.api_wrapper.raw_results(
                query,
                self.count,
                self.freshness,
                self.summary,
                self.include,
                self.exclude,
            )
        except Exception as e:
            return f"Error: {repr(e)}"
        
        if self.include_images:
            cleaned_results = self.api_wrapper.clean_results_with_images(raw_results)
        else:
            cleaned_results = self.api_wrapper.clean_results(raw_results)
            
        return cleaned_results

    async def _arun(
        self,
        query: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs
    ) -> Union[List[Dict[str, str]], str]:
        """Execute the web search asynchronously.
        
        Args:
            query: The search query string, or can be passed as kwargs["args"]["query"]
            run_manager: Optional callback manager
            
        Returns:
            List of cleaned search results with page information and optional images
        """
        # Handle both direct query string and args format
        if query is None and "args" in kwargs:
            args = kwargs["args"]
            if isinstance(args, dict) and "query" in args:
                query = args["query"]
            elif isinstance(args, str):
                query = args
            elif isinstance(args, list) and len(args) > 0:
                # Handle list format - use the first item as the query
                query = args[0]
                
        if not query:
            return "Error: No search query provided"
            
        try:
            raw_results = await self.api_wrapper.raw_results_async(
                query,
                self.count,
                self.freshness,
                self.summary,
                self.include,
                self.exclude,
            )
        except Exception as e:
            return f"Error: {repr(e)}"
        
        if self.include_images:
            cleaned_results = self.api_wrapper.clean_results_with_images(raw_results)
        else:
            cleaned_results = self.api_wrapper.clean_results(raw_results)
            
        return cleaned_results 