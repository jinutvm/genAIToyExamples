import os
import json
import asyncio

from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

class BlogPost(BaseModel):
    """
    Represents the data structure of a blog post.
    """
    link: str
    title: str
    author: str
    date: str
    page_content: str

class LLMBasedWebCrawler:
    def __init__(self, headless: bool = False):
        """
        Initialize the LLM-based web crawler.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.browser_config = BrowserConfig(headless=headless)
        self.crawler = None

    def _get_crawler_config(self) -> CrawlerRunConfig:
        """
        Create and return the crawler configuration.
        
        Returns:
            CrawlerRunConfig: The configured crawler settings
        """
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            page_timeout=80000,
            extraction_strategy=LLMExtractionStrategy(
                llm_config=LLMConfig(
                    provider="groq/qwen-qwq-32b",
                    api_token=os.getenv("GROQ_API_KEY"),
                ),
                schema=BlogPost.model_json_schema(),
                extraction_type="schema",
                instruction="""From the crawled content, extract Title, Author if any, Date of the blog, page_content of the blog.""",
            ),
        )

    async def crawl_url(self, url: str) -> dict:
        """
        Crawl a specific URL and extract structured data.
        
        Args:
            url (str): The URL to crawl
            
        Returns:
            dict: The extracted content
        """
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=self._get_crawler_config()
            )
            return json.loads(result.extracted_content) if result.extracted_content else None

    async def crawl_multiple_urls(self, urls: list) -> list:
        """
        Crawl multiple URLs and extract structured data from each.
        
        Args:
            urls (list): List of URLs to crawl
            
        Returns:
            list: List of extracted content from each URL
        """
        results = []
        for url in urls:
            result = await self.crawl_url(url)
            if result:
                results.append(result)
        return results

async def main():
    # Example usage
    crawler = LLMBasedWebCrawler(headless=False)
    
    # Single URL example
    url = "https://invicara.com/resources/blog/transforming-building-information-models"
    result = await crawler.crawl_url(url)
    print("Single URL result:", result)
    
    # Multiple URLs example
    urls = [
        "https://invicara.com/resources/blog/transforming-building-information-models",
        # Add more URLs here
    ]
    results = await crawler.crawl_multiple_urls(urls)
    print("Multiple URL results:", results)

if __name__ == "__main__":
    asyncio.run(main())