import asyncio
# import nest_asyncio
# nest_asyncio.apply()

async def crawl_page(url):
    print('crawling {}'.format(url))
    sleep_time = int(url.split('_')[-1])
    await asyncio.sleep(sleep_time)
    print('OK {}'.format(url))

async def main(urls):
    for url in urls:
        await crawl_page(url)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(['url_1', 'url_2', 'url_3', 'url_4']))
# or
# asyncio.run(main(['url_1', 'url_2', 'url_3', 'url_4']))
