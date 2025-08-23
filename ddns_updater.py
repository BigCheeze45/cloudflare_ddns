"""
Dynamic DNS updater for Cloudflare.

This script monitors your public IP address and automatically updates a specified
Cloudflare DNS record when your IP changes. Useful for maintaining access to
home servers or services when using dynamic IP addresses from ISPs.

Required environment variables (.env file):
- CLOUDFLARE_EMAIL: Your Cloudflare account email
- CLOUDFLARE_API_TOKEN: Cloudflare API token with DNS edit permissions
- ZONE_ID: The zone ID for your domain
- RECORD_ID: The DNS record ID to update

The script will:
1. Fetch your current public IP address
2. Retrieve the current DNS record from Cloudflare
3. Compare IPs and update the DNS record if they differ
"""

import requests
from cloudflare import Cloudflare


def get_public_ip(raise_for_status: bool = True):
    """
    Get the current public IP address using [ifconfig.co](https://ifconfig.co/) service.

    Args:
        raise_for_status (bool, optional): Whether to raise an exception for HTTP errors.
                                         Defaults to `True`.

    Returns:
        dict: JSON response containing IP address information. Typically includes
              keys like 'ip', 'country', 'city', etc.

    Raises:
        requests.exceptions.HTTPError: If raise_for_status is True and the server returns
                                     an HTTP error status code (4xx, 5xx).
    """
    response = requests.get(
        "https://ifconfig.co/", headers={"Accept": "application/json"}
    )

    if raise_for_status:
        response.raise_for_status()

    return response.json()


def update_dns_ip(raise_for_status: bool = True, **secrets):
    """
    Update Cloudflare DNS record with current public IP address if it has changed.

    Args:
        **secrets: Keyword arguments containing Cloudflare API credentials and identifiers:
            CLOUDFLARE_EMAIL (str): Cloudflare account email address.
            CLOUDFLARE_API_TOKEN (str): Cloudflare API token with DNS edit permissions.
            ZONE_ID (str): The zone ID for the domain containing the DNS record.
            RECORD_ID (str): The DNS record ID to update.

    Returns:
        cloudflare.types.dns.Record or None: Updated DNS record object if IP was changed,
                                           None if no update was needed.

    Raises:
        KeyError: If required secrets (CLOUDFLARE_API_TOKEN, ZONE_ID, RECORD_ID) are missing.
        cloudflare.APIError: If Cloudflare API request fails (invalid credentials,
                           permissions, or API limits exceeded).
    """
    # Set up Cloudflare client
    cloudflare_client = Cloudflare(
        api_email=secrets.get("CLOUDFLARE_EMAIL"),
        api_token=secrets["CLOUDFLARE_API_TOKEN"],
        default_headers={
            "Authorization": f"Bearer {secrets['CLOUDFLARE_API_TOKEN']}",
        },
    )

    # Get Cloudflare DNS record
    record = cloudflare_client.dns.records.get(
        zone_id=secrets["ZONE_ID"], dns_record_id=secrets["RECORD_ID"]
    )

    # Get our public IP
    pub_ip_info = get_public_ip(raise_for_status)

    if record.content != pub_ip_info["ip"]:
        # Our public IP has changed & Cloudflare DNS record needs to be updated
        return cloudflare_client.dns.records.update(
            name=record.name,
            type=record.type,
            dns_record_id=record.id,
            content=pub_ip_info["ip"],  # set new IP
            zone_id=secrets["ZONE_ID"],
        )
