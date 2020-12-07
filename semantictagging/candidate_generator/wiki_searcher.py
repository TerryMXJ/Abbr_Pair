#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import asyncio
import traceback
import logging

from aiohttp_retry import RetryClient, RetryOptions
import async_timeout

from .wiki_entry import WikiEntry
from .wiki_page import WikiPage


logging.basicConfig(level = logging.INFO, format = '[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

class WikiSearcher:
    def __init__(self, api, proxy=None, pool_size=63, timeout=20, retry_attempts=3):
        self.api = api
        self.proxy = proxy
        self.pool_size = pool_size
        self.timeout = timeout
        self.retry_options = RetryOptions(
            attempts=retry_attempts,
            max_timeout=timeout,
            statuses={stat for stat in range(100, 600) if stat != 200},
            exceptions={Exception}
        )
        self.entry_cache = dict()
        self.page_cache = dict()

    async def __search_entries(self, title, page_limit=25):
        if title in self.entry_cache:
            return self.entry_cache[title]
        entries = None
        params = {
            'format': 'json',
            'action': 'query',
            'list': 'search',
            'srprop': 'snippet|sectiontitle',
            'srlimit': page_limit,
            'srsearch': title,
        }
        async with asyncio.Semaphore(self.pool_size), async_timeout.timeout(self.timeout):
            async with RetryClient(retry_options=self.retry_options) as client:
                try:
                    async with client.get(self.api, proxy=self.proxy, params=params) as response:  
                        json_res = await response.json()
                        entries = []
                        for entry in json_res["query"]["search"]:
                            entries.append(WikiEntry(entry["ns"], entry["title"], entry["pageid"], entry["snippet"], entry.get("sectiontitle", None)))
                            self.entry_cache[title] = entry
                except Exception as e:
                    traceback.print_exc()
                    logger.error(f"failed title: {title}")
        return entries

    def search_entries(self, titles, page_limit=25):
        title2entries = dict()
        waiting_titles = list(titles)
        for _ in range(self.retry_options.attempts):
            if len(waiting_titles) > 0:
                loop = asyncio.get_event_loop()
                tasks = [self.__search_entries(title, page_limit=page_limit) for title in waiting_titles]
                results = loop.run_until_complete(asyncio.gather(*tasks))
                for title, result in zip(waiting_titles, results):
                    if result is None:
                        continue
                    title2entries[title] = result
                    waiting_titles.remove(title)
        return title2entries

    async def __fetch_page(self, title):
        if title in self.page_cache:
            return self.page_cache[title]
        page = None
        if type(title) == int:
            params = {
                'pageid': title,
                'format': 'json',
                'action': 'parse',
                'prop': 'text|categories',
                'formatversion': 2,
                'redirects': 1
            }
        else:
            params = {
                'page': title,
                'format': 'json',
                'action': 'parse',
                'prop': 'text|categories',
                'formatversion': 2,
                'redirects': 1
            }
        async with asyncio.Semaphore(self.pool_size), async_timeout.timeout(self.timeout):
            async with RetryClient(retry_options=self.retry_options) as client:
                try:
                    async with client.get(self.api, proxy=self.proxy, params=params) as response:
                        json_res = await response.json()
                        if "error" not in json_res and "parse" in json_res:
                            page = WikiPage(
                                json_res["parse"]["title"],
                                json_res["parse"]["pageid"],
                                json_res["parse"]["redirects"],
                                json_res["parse"]["text"],
                                json_res["parse"]["categories"],
                            )
                        # page = json_res
                except Exception as e:
                    traceback.print_exc()
                    logger.error(f"failed title: {title}")
        return page

    def fetch_page(self, titles):
        title2page = dict()
        waiting_titles = list(titles)
        for _ in range(self.retry_options.attempts):
            if len(waiting_titles) > 0:
                loop = asyncio.get_event_loop()
                tasks = [self.__fetch_page(title) for title in waiting_titles]
                results = loop.run_until_complete(asyncio.gather(*tasks))
                for title, result in zip(waiting_titles, results):
                    if result is None:
                        continue
                    title2page[title] = result
                    waiting_titles.remove(title)
        return title2page

    