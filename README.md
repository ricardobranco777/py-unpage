![Build Status](https://github.com/ricardobranco777/unpage/actions/workflows/ci.yml/badge.svg)

# unpage

Get all pages of an URL

## Requirements

- [requirements-dev.txt](requirements-dev.txt)

## Usage

```
usage: unpage.py [-h] [-H HEADERS] [-P PARAM_PAGE] [-D DATA_KEY] [-N NEXT_KEY] [-L LAST_KEY] url

positional arguments:
  url

options:
  -h, --help            show this help message and exit
  -H HEADERS, --headers HEADERS
                        HTTP headers in the format 'Key: Value'. Use multiple times for multiple headers. (default: None)
  -P PARAM_PAGE, --param-page PARAM_PAGE
                        Name of the parameter that represents the page number. (default: page)
  -D DATA_KEY, --data-key DATA_KEY
                        Key to access the data in the JSON response. (default: None)
  -N NEXT_KEY, --next-key NEXT_KEY
                        Key to access the next page link in the JSON response. (default: None)
  -L LAST_KEY, --last-key LAST_KEY
                        Key to access the last page link in the JSON response. (default: None)
```

## Examples:

- `--data-key repositories https://registry.opensuse.org/v2/_catalog?n=50`
- `https://src.opensuse.org/api/v1/repos/issues/search?limit=1`
- `--data-key issues_created --next-key pagination_issues_created.next --last_key pagination_issues_created.last 'https://code.opensuse.org/api/0/user/rbranco/issues?assignee=1&per_page=1'`
