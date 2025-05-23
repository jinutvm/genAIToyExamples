import os
import json
import asyncio

from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig,BrowserConfig,CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

class blogPost(BaseModel):
    """
    Represents the data structure of a blog post.
    """

    link: str
    title: str
    author: str
    date: str
    page_content: str


async def extract_structured_data_using_llm():
    browser_config = BrowserConfig(headless=False)  # or False to see the browser



    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        page_timeout=80000,
        extraction_strategy=LLMExtractionStrategy(
            llm_config = LLMConfig(provider="groq/qwen-qwq-32b",api_token=os.getenv("GROQ_API_KEY"),),
            schema=blogPost.model_json_schema(),
            extraction_type="schema",
            # instruction="""From the crawled content, extract Title, Author if any, Date of the blog, page_content of the blog in markdown format
            # In the page content avoid the title, author, date.""",
            instruction="""From the crawled content, extract Title, Author if any, Date of the blog, page_content of the blog.
            """,
            # extra_args=extra_args,
        ),
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://invicara.com/resources/blog/transforming-building-information-models",
            config=crawler_config
        )
        # print(result.markdown)
        print(result.extracted_content)

if __name__ == "__main__":

    asyncio.run(extract_structured_data_using_llm())