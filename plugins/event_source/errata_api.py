import asyncio
import logging
import datetime
from typing import Any


BASE_URL = {
    "https://access.redhat.com/hydra/rest/securitydata"
}



async def main(queue: asyncio.Queue[Any], args: dict[str, Any]) -> None:
    """Poll the errata API and send events with new errata."""

    logger = logging.getLogger()
    logger.info("Processing errata queue")

    delay = int(args.get("interval", 1))

    common_get_args = {}
    if not verify_ssl:
        common_get_args["ssl"] = True

    poll_since = datetime.datetime.now()

    while True:
        endpoint_url = BASE_URL + "csaf.json&after=" + poll_since.isoformat()
        logger.info("Retrieving errata from " + endpoint_url)

        poll_since = datetime.datetime.now()

        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint_url) as resp:
                for errata in resp:
                    await queue.put(
                        {
                            "errata_api": {
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