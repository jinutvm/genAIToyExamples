import asyncio
# from crawl4ai import *
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# async def main():
#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(
#             url="https://invicara.com/resources/blog/transforming-building-information-models",
#         )
#         print(result.markdown)

async def main():
    browser_conf = BrowserConfig(headless=False)  # or False to see the browser

    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.4, threshold_type="fixed")
    )

    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url="https://invicara.com/resources/blog/transforming-building-information-models",
            config=run_conf
        )
        print(result.markdown.fit_markdown)

if __name__ == "__main__":
    asyncio.run(main())