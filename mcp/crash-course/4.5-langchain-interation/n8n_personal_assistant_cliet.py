from mcp.client.sse import sse_client
from mcp import ClientSession, StdioServerParameters

import requests
from random import randint
import asyncio
import nest_asyncio

nest_asyncio.apply()
# Lets make concorrent requests 

url = "http://localhost:5678/webhook/concurrency_testing"

tunnel_url = "https://boss-fw-associate-marks.trycloudflare.com"
url = f"{tunnel_url}/webhook/concurrency_testing"


def make_request():

    rand1 = randint(10, 100)
    rand2 = randint(10, 100)
    rand3 = randint(10, 100)

    payload = {
        "rand1": rand1,
        "rand2": rand2,
        "rand3": rand3
    }

    print (f"Payload: {payload}")

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        # print(f"Response: {response}")
        return response.text
    else:
        print(f"Failed to get a valid response, status code: {response.status_code}")


data = make_request()

# lets make 10 requests concurrently
async def make_concurrent_requests(num_requests: int):
    tasks = [asyncio.to_thread(make_request) for _ in range(num_requests)]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(make_concurrent_requests(30))

