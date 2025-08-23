# Dynamic DNS updater for Cloudflare

This script monitors your public IP address and automatically updates a specified
Cloudflare DNS record when your IP changes. Useful for maintaining access to
home servers or services when using dynamic IP addresses from ISPs.

This project is a Python implemtation of [Paul Sørensen's blog post](
    https://paulsorensen.io/configure-ddns-with-cloudflare/) and does
    not utilize Cloudflare Workers.

### Prerequisites
This script is helpful if the following conditions apply:

1. You have a domain.
2. Domain points to a server with a dynamic IP.
2. **DNS management is done via Cloudflare**. This script will not work as is if DNS records are managed somewhere else.

## Getting Started
If you use pip:

```shell
pip install --no-deps -r requirements.txt
```

If you use [poetry](https://python-poetry.org/):

```shell
poetry install
```
### Example `main.py`
```python
import requests
from dotenv import dotenv_values
from cloudflare import CloudflareError

from ddns_updater import update_dns_ip

if __name__ == "__main__":
    # Load secrets from .env file
    secrets = dotenv_values()
    try:
        record = update_dns_ip(**secrets)
        if record:
            # DNS updated
            pass
    except CloudflareError as ce:
        pass
    except requests.exceptions.HTTPError as htte:
        pass
    except Exception as e:
        pass
```