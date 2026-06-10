import asyncio
import aiohttp
import logging
import datetime
from typing import Any


BASE_URL = "https://access.redhat.com/hydra/rest/securitydata/"



async def main(queue: asyncio.Queue[Any], args: dict[str, Any]) -> None:
    """Poll the errata API and send events with new errata."""

    logger = logging.getLogger()
    logger.info("Processing errata queue")

    delay = int(args.get("interval", 60))
    # Undocumented parameter for testing
    resend_days = int(args.get("resend_days", 0))

    poll_since = datetime.datetime.now() - datetime.timedelta(days=resend_days)

    while True:
        endpoint_url = "{}csaf.json?after={}".format(BASE_URL, poll_since.isoformat())
        logger.info("Retrieving errata from {}".format(endpoint_url))
        print("Retrieving errata from {}".format(endpoint_url))

        poll_since = datetime.datetime.now()

        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint_url) as resp:
                if resp.status == 200:
                    errata_data = await resp.json()
                    # print(errata_data)
                    for errata in errata_data:
                        await queue.put(
                            {
                                "body": {
                                    "data" : errata,
                                },
                            },
                        )

        await asyncio.sleep(delay)



if __name__ == "__main__":

    class MockQueue:
        async def put(self, event):
            print(event)

    asyncio.run(main(MockQueue(), {}))