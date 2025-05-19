import json
import os
from typing import Dict, List, Optional

import aiohttp
import requests
from pydantic import BaseModel, Field, SecretStr

BOCHA_API_URL = "https://api.bochaai.com/v1/web-search"


class BochaSearchAPIWrapper(BaseModel):
    """Wrapper for the Bocha Web Search API.

    To use, you should have the ``bocha_api_key`` set as an environment variable.
    """

    bocha_api_key: SecretStr = Field(default_factory=lambda: SecretStr(os.environ.get("BOCHA_API_KEY", "")))

    def raw_results(
        self,
        query: str,
        count: Optional[int] = 10,
        freshness: Optional[str] = "noLimit",
        summary: Optional[bool] = True,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> Dict:
        """Get search results from the Bocha Web Search API."""
        params = {
            "query": query,
            "count": count,
            "freshness": freshness,
            "summary": summary,
        }
        
        if include:
            params["include"] = "|".join(include)
        
        if exclude:
            params["exclude"] = "|".join(exclude)
        
        headers = {
            "Authorization": f"Bearer {self.bocha_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(
            BOCHA_API_URL,
            headers=headers,
            json=params,
        )
        response.raise_for_status()
        return response.json()

    async def raw_results_async(
        self,
        query: str,
        count: Optional[int] = 10,
        freshness: Optional[str] = "noLimit",
        summary: Optional[bool] = True,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> Dict:
        """Get results from the Bocha Web Search API asynchronously."""

        # Function to perform the API call
        async def fetch() -> str:
            params = {
                "query": query,
                "count": count,
                "freshness": freshness,
                "summary": summary,
            }
            
            if include:
                params["include"] = "|".join(include)
            
            if exclude:
                params["exclude"] = "|".join(exclude)
                
            headers = {
                "Authorization": f"Bearer {self.bocha_api_key.get_secret_value()}",
                "Content-Type": "application/json",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(BOCHA_API_URL, headers=headers, json=params) as res:
                    if res.status == 200:
                        data = await res.text()
                        return data
                    else:
                        raise Exception(f"Error {res.status}: {res.reason}")

        results_json_str = await fetch()
        return json.loads(results_json_str)

    def clean_results(self, raw_results: Dict) -> List[Dict]:
        """Clean results from Bocha Web Search API."""
        if raw_results.get("code") != 200 or not raw_results.get("data"):
            return [{"error": f"Search API request failed: {raw_results.get('msg', 'Unknown error')}"}]
        
        web_pages = raw_results["data"].get("webPages", {}).get("value", [])
        if not web_pages:
            return [{"error": "No results found."}]
        
        clean_results = []
        for idx, page in enumerate(web_pages, start=1):
            clean_result = {
                "type": "page",
                "citation": idx,
                "title": page.get("name", ""),
                "url": page.get("url", ""),
                "content": page.get("snippet", "") if not page.get("summary") else page.get("summary", ""),
                "site_name": page.get("siteName", ""),
                "site_icon": page.get("siteIcon", ""),
                "date_published": page.get("datePublished", "") or page.get("dateLastCrawled", ""),
            }
            clean_results.append(clean_result)
        return clean_results
        
    def clean_results_with_images(self, raw_results: Dict) -> List[Dict]:
        """Clean results from Bocha Web Search API including images."""
        if raw_results.get("code") != 200 or not raw_results.get("data"):
            return [{"error": f"Search API request failed: {raw_results.get('msg', 'Unknown error')}"}]
        
        results = []
        
        # Process web pages
        web_pages = raw_results["data"].get("webPages", {}).get("value", [])
        for idx, page in enumerate(web_pages, start=1):
            clean_result = {
                "type": "page",
                "citation": idx,
                "title": page.get("name", ""),
                "url": page.get("url", ""),
                "content": page.get("snippet", "") if not page.get("summary") else page.get("summary", ""),
                "site_name": page.get("siteName", ""),
                "site_icon": page.get("siteIcon", ""),
                "date_published": page.get("datePublished", "") or page.get("dateLastCrawled", ""),
            }
            results.append(clean_result)
        
        # Process images
        images = raw_results["data"].get("images", {}).get("value", [])
        for image in images:
            image_result = {
                "type": "image",
                "image_url": image.get("contentUrl", ""),
                "thumbnail_url": image.get("thumbnailUrl", ""),
                "host_page_url": image.get("hostPageUrl", ""),
                "width": image.get("width", 0),
                "height": image.get("height", 0),
            }
            results.append(image_result)
        return results


if __name__ == "__main__":
    wrapper = BochaSearchAPIWrapper()
    results = wrapper.raw_results("阿里巴巴2024年ESG报告", summary=True)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    cleaned_results = wrapper.clean_results_with_images(results)
    print(json.dumps(cleaned_results, indent=2, ensure_ascii=False))
