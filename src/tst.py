import logging
import asyncio
import httpx
from url import URLFactory
from utils import get_sync_response_json, get_async_responses_json

log = logging.getLogger(__name__)

from wrapper import IMFWrapper



    
    
def main():
    
    # imf = IMFWrapper()
    # datasets = list(imf.datasets.keys())
    
    # async def get_info(datasets):
    
    #     log.debug(f"Asking for {len(datasets)} datasets")
        
    #     async with httpx.AsyncClient() as client:
    #         async with asyncio.TaskGroup() as tg:
                
    #             responses = [tg.create_task(client.get(IMFUrl.data_structure(dataset))) 
    #                             for dataset in datasets]
                    
    #     log.debug(f"Got {len(responses)} responses")
    
    imf = IMFWrapper()
    urls = [URLFactory.data_structure(dataset) for dataset in imf.datasets.keys()]



    responses = get_async_responses_json(urls)
    
    # responses = [get_sync_response_json(url) for url in urls]
    for r in responses:
        print(r.keys())
       
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s : %(name)s : %(funcName)s : %(message)s')
    
    main()
    