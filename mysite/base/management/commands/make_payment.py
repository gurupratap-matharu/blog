import base64
import json
import logging
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand

import requests


logger = logging.getLogger(__name__)

BIN = "450799"

grouper = "Ventanita"
developer = "Gurupratap"
BASE_URL = "https://developers-ventasonline.payway.com.ar/api/v2"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            help="Token received from front end using public key",
        )

        parser.add_argument(
            "-a",
            "--amount",
            type=int,
            help="Amount to be charged",
        )

    def handle(self, *args, **options):

        logger.info(args)
        logger.info(options)

        token = options.get("token", "")
        amount = options.get("amount", 0)
        site_transaction_id = str(uuid.uuid4())
        url = f"{BASE_URL}/payments"

        headers = {
            "apikey": settings.PAYWAY_PRIVATE_KEY,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        payload = {
            "site_transaction_id": site_transaction_id,
            "token": token,
            "user_id": "Gurupratap",
            "payment_method_id": 1,
            "bin": BIN,
            "amount": amount,
            "currency": "ARS",
            "installments": 1,
            "description": "Pasajes de micro",
            "payment_type": "single",
            "sub_payments": [],
            "apiKey": settings.PAYWAY_PRIVATE_KEY,
            "Content-Type": "application/json",
        }

        logger.info("url:%s" % url)
        logger.info("headers:%s" % headers)
        logger.info("payload:%s" % payload)

        response = requests.post(url, headers=headers, json=payload)
        logger.info("status:%s" % response.status_code)
        logger.info("response.json():%s" % response.json())

        return response

    def _generate_xsource_header(self, grouper, developer):
        xsource_obj = {
            "service": "SDK-NODE",
            "grouper": grouper,
            "developer": developer,
        }
        # Convert the dictionary to a JSON string
        json_str = json.dumps(xsource_obj)
        # Encode the JSON string to bytes and then to base64
        base64_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
        return base64_str
