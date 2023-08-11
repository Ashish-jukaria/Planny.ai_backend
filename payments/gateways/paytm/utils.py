import requests
import json
import paytmchecksum
import phurti.settings as settings

PAYTM_MID = settings.PAYTM_MERCHANT_ID
PAYTM_MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
PAYTM_WEBISTE = settings.PAYTM_WEBSITE
PAYTM_HOST = settings.PAYTM_HOST


def create_payment_order(amount, orderid, userid):
    paytmParams = dict()
    paytmParams["body"] = {
        "requestType": "Payment",
        "mid": PAYTM_MID,
        "websiteName": PAYTM_WEBISTE,
        "orderId": str(orderid),
        "callbackUrl": "",
        "txnAmount": {
            "value": float(amount),
            "currency": "INR",
        },
        "userInfo": {"customerId": userid, "orderId": orderid},
    }
    checksum = paytmchecksum.generateSignature(
        json.dumps(paytmParams["body"]), PAYTM_MERCHANT_KEY
    )

    paytmParams["head"] = {"signature": checksum}
    print(paytmParams)
    post_data = json.dumps(paytmParams)
    # for Staging
    url = f"{PAYTM_HOST}/theia/api/v1/initiateTransaction?mid={PAYTM_MID}&orderId={orderid}"
    response = requests.post(
        url, data=post_data, headers={"Content-type": "application/json"}
    ).json()
    return response


def transaction_detail(order_id):
    import requests
    import json
    import paytmchecksum

    # initialize a dictionary
    paytmParams = dict()
    # body parameters
    paytmParams["body"] = {
        "mid": PAYTM_MID,
        "orderId": order_id,
    }
    checksum = paytmchecksum.generateSignature(
        json.dumps(paytmParams["body"]), PAYTM_MERCHANT_KEY
    )
    paytmParams["head"] = {"signature": checksum}
    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    # for Staging
    url = f"{PAYTM_HOST}/v3/order/status"
    response = requests.post(
        url, data=post_data, headers={"Content-type": "application/json"}
    ).json()
    del response["body"]["mid"]
    return response
