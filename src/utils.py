from typing import Iterable
import httpx
from json import JSONDecodeError
import asyncio

import logging
log = logging.getLogger(__name__)

def is_non_string_iterable(x: object) -> bool:
    return isinstance(x, Iterable) and not isinstance(x, str)


def _extract_json_from_response(response: httpx.Response):
    
    if response.status_code != 200:
        log.error(f"Request {response.url} failed with status code {response.status_code}.")
    
    try:
        return response.json()
    except JSONDecodeError:
        log.error(f"Response from {response.url} is not a valid JSON object.")

def get_sync_response_json(url: str) -> dict:
    
    with httpx.Client() as client:
        response = client.get(url)
    
    json_content = _extract_json_from_response(response)
    return json_content

def get_async_responses_json(urls: Iterable[str]) -> dict:
    
    async def make_requests(urls):
        tasks = []
        batch_size = 10
        total = len(urls)
        async with httpx.AsyncClient() as client:
            
            for k in range(0, total, batch_size):
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(asyncio.sleep(10))
                    
                    tasks.extend([tg.create_task(client.get(url)) for url in urls[k:k+batch_size]])
                    
        
        return [_extract_json_from_response(task.result()) for task in tasks]
    
    json_contents = asyncio.run(make_requests(urls))
        
    return json_contents