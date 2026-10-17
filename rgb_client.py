import json
import time
import urllib.request
import urllib.error


STUDENT_NODE = "http://localhost:3002"
LANDLORD_NODE = "http://localhost:3004"

PROXY = "rpcs://proxy.iriswallet.com/0.2/json-rpc"

STUSD_ASSET_ID = "rgb:cTZJebk3-Es~AA63-kUOxEqS-dtu9DCl-gDjmc5K-dTW2Wn0"


def _get_json(url: str):
    request = urllib.request.Request(
        url,
        method="GET",
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        message = error.read().decode("utf-8")
        raise RuntimeError(message)


def _post_json(url: str, data: dict):
    body = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        message = error.read().decode("utf-8")
        raise RuntimeError(message)


def create_landlord_invoice():
    """
    Creates a fresh generic RGB invoice on landlord2.

    The invoice does not specify STUSD in advance,
    so landlord2 can receive STUSD even if this is
    its first time receiving that asset.
    """

    expiry = int(time.time()) + 3600

    result = _post_json(
        f"{LANDLORD_NODE}/rgbinvoice",
        {
            "min_confirmations": 1,
            "asset_id": None,
            "assignment": None,
            "expiration_timestamp": expiry,
            "witness": False,
            "transport_endpoints": [
                PROXY
            ],
        },
    )

    return result


def send_stusd_payment(amount: int):
    """
    Creates a fresh landlord invoice and sends
    STUSD from studentcopilot to landlord2.
    """

    invoice_data = create_landlord_invoice()

    recipient_id = invoice_data["recipient_id"]

    expiry = int(time.time()) + 3600

    result = _post_json(
        f"{STUDENT_NODE}/sendrgb",
        {
            "donation": False,
            "fee_rate": 5,
            "min_confirmations": 1,
            "expiration_timestamp": expiry,
            "recipient_map": {
                STUSD_ASSET_ID: [
                    {
                        "recipient_id": recipient_id,
                        "assignment": {
                            "type": "Fungible",
                            "value": amount,
                        },
                        "transport_endpoints": [
                            PROXY
                        ],
                    }
                ]
            },
        },
    )

    return result


def send_rent_payment():

    return send_stusd_payment(250)

def get_stusd_balance():
    result = _post_json(
        f"{STUDENT_NODE}/assetbalance",
        {
            "asset_id": STUSD_ASSET_ID
        },
    )

    return result