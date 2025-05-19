# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os

from langchain_community.tools import BraveSearch, DuckDuckGoSearchResults
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper, BraveSearchWrapper

from src.config import SearchEngine, SELECTED_SEARCH_ENGINE
from src.tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchResultsWithImages,
)
from src.tools.bocha_search.bocha_search_results import BochaSearchResultsWithImages
from src.tools.decorators import create_logged_tool

logger = logging.getLogger(__name__)

# Create logged versions of the search tools
LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)
LoggedBochaSearch = create_logged_tool(BochaSearchResultsWithImages)
LoggedDuckDuckGoSearch = create_logged_tool(DuckDuckGoSearchResults)
LoggedBraveSearch = create_logged_tool(BraveSearch)
LoggedArxivSearch = create_logged_tool(ArxivQueryRun)


# Get the selected search tool
def get_web_search_tool(max_search_results: int):
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        return LoggedTavilySearch(
            name="web_search",
            max_results=max_search_results,
            include_raw_content=True,
            include_images=True,
            include_image_descriptions=True,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BOCHA.value:
        return LoggedBochaSearch(
            name="web_search",
            description=(
                "A powerful web search tool using Bocha API that finds current information from the internet. "
                "Use this to search for facts about recent events, news, current information, "
                "or any topic requiring up-to-date web results. Returns detailed web page content, summaries, "
                "and optionally images. Input should be a search query string, with more specific "
                "queries giving better results."
            ),
            count=max_search_results,
            summary=True,
            include_images=True,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        return LoggedDuckDuckGoSearch(name="web_search", max_results=max_search_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        return LoggedBraveSearch(
            name="web_search",
            search_wrapper=BraveSearchWrapper(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
                search_kwargs={"count": max_search_results},
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        return LoggedArxivSearch(
            name="web_search",
            api_wrapper=ArxivAPIWrapper(
                top_k_results=max_search_results,
                load_max_docs=max_search_results,
                load_all_available_meta=True,
            ),
        )
    else:
        raise ValueError(f"Unsupported search engine: {SELECTED_SEARCH_ENGINE}")


if __name__ == "__main__":
    results = LoggedDuckDuckGoSearch(
        name="web_search", max_results=3, output_format="list"
    ).invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))
