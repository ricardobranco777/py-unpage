"""
unpage
"""

import argparse
import asyncio
import json
import os
import sys
from functools import reduce
from operator import getitem
from typing import Any, Callable
from urllib.parse import urlparse, urlsplit, parse_qs

import httpx  # type: ignore[import]
from requests.utils import parse_header_links


__version__ = "0.1.0"


def xgetitem(*keys: str | int) -> Callable[[Any], Any]:
    """
    Create a nested item getter function.

    This function takes a variable number of keys and returns a callable
    object that, when given a nested structure (like a dictionary), retrieves
    the value at the specified keys.

    Parameters:
    *keys (hashable): The keys to navigate the nested structure.

    Returns:
    callable: A function that can be applied to a nested structure to retrieve
              the value at the specified keys.

    Example:
    >>> nested_dict = {'a': {'b': {'c': 42}}}
    >>> getter = xgetitem('a', 'b', 'c')
    >>> getter(nested_dict)
    42

    >>> nested_list = [{'key': {'nested_key': 'value'}}]
    >>> getter = xgetitem(0, 'key', 'nested_key')
    >>> getter(nested_list)
    'value'
    """
    return lambda item: reduce(getitem, keys, item)


async def log_response(response) -> None:
    """
    Log response
    """
    if not os.getenv("DEBUG"):
        return
    request = response.request
    log = f"> {request.method} {request.url} {response.http_version}\n"
    for header, value in request.headers.items():
        log += f"> {header}: {value}\n"
    log += f"< {response.http_version} {response.status_code}\n"
    for header, value in response.headers.items():
        log += f"> {header}: {value}\n"
    await response.aread()
    log += f"< {response.text}"
    print(log, file=sys.stderr)


async def unpage(  # pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments
    url: str,
    headers: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    param_page: str = "page",
    data_key: str | None = None,
    next_key: str | None = None,
    last_key: str | None = None,
) -> list[Any]:
    """
    Get all paginated responses
    """
    entries: list[dict[str, Any]] = []

    if headers is None:
        headers = {}
    if params is None:
        params = {}

    base_url = "://".join(urlsplit(url)[:2])

    async with httpx.AsyncClient(
        event_hooks={"response": [log_response]},
        follow_redirects=True,
        headers=headers,
    ) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        entries = data if data_key is None else data[data_key]

        next_link = last_link = None
        if "Link" in response.headers:
            links = parse_header_links(response.headers["Link"])
            next_link = next((x["url"] for x in links if x.get("rel") == "next"), None)
            last_link = next((x["url"] for x in links if x.get("rel") == "last"), None)
        elif next_key is not None and last_key is not None:
            next_link = xgetitem(*next_key.split("."))(data)
            last_link = xgetitem(*last_key.split("."))(data)

        if last_link is not None:
            if last_link.startswith("/"):
                last_link = f"{base_url}{last_link}"
            last_page = int(parse_qs(urlparse(last_link).query)[param_page][0])

            async def get_page(page: int) -> list[dict[str, Any]]:
                xparams = dict(params)
                xparams[param_page] = page
                response = await client.get(url, params=xparams)
                response.raise_for_status()
                data = response.json()
                return data if data_key is None else data[data_key]

            tasks = [get_page(page) for page in range(2, last_page + 1)]
            results = await asyncio.gather(*tasks)
            for result in results:
                entries.extend(result)
        else:
            while next_link is not None:
                if next_link.startswith("/"):
                    next_link = f"{base_url}{next_link}"
                response = await client.get(next_link, params=params)
                response.raise_for_status()
                data = response.json()
                entries.extend(data if data_key is None else data[data_key])
                if "Link" not in response.headers:
                    break
                links = parse_header_links(response.headers["Link"])
                next_link = next(
                    (x["url"] for x in links if x.get("rel") == "next"), None
                )
        return entries


def main():
    """
    Main
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("url")

    parser.add_argument(
        "-H",
        "--headers",
        action="append",
        help="HTTP headers in the format 'Key: Value'. Use multiple times for multiple headers.",
    )
    parser.add_argument(
        "-P",
        "--param-page",
        default="page",
        help="Name of the parameter that represents the page number.",
    )
    parser.add_argument(
        "-D", "--data-key", help="Key to access the data in the JSON response."
    )
    parser.add_argument(
        "-N",
        "--next-key",
        help="Key to access the next page link in the JSON response.",
    )
    parser.add_argument(
        "-L",
        "--last-key",
        help="Key to access the last page link in the JSON response.",
    )

    args = parser.parse_args()

    headers = (
        {
            k.strip(): v.strip()
            for k, v in (header.split(":", 1) for header in args.headers)
        }
        if args.headers
        else {}
    )
    headers["Accept"] = "application/json"
    headers["User-Agent"] = f"unpage/{__version__}"

    result = asyncio.run(
        unpage(
            args.url,
            headers=headers,
            param_page=args.param_page,
            data_key=args.data_key,
            next_key=args.next_key,
            last_key=args.last_key,
        )
    )

    print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
