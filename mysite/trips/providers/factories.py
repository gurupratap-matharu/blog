"""
A Class that mocks the api response.
"""

import random
from datetime import timedelta

from django.utils import timezone


class ProsysFactory:

    LOCATIONS = (
        "Retiro",
        "Liniers",
        "Talar",
        "Mendoza",
        "Mar del Plata",
        "Cordoba",
        "San Juan",
        "Rosario",
    )

    COMPANIES = ("CATA", "Andesmar", "Balut", "Flecha Bus")

    def _seat(self):
        return str(random.randint(1, 44))

    def _ticket_number(self):
        return str(random.randrange(10000, 20000))

    def _ticket_id(self):
        return str(random.randrange(60000, 80000))

    def _company(self):
        return random.choice(self.COMPANIES)

    def _location(self):
        return random.choice(self.LOCATIONS)

    def _departure(self):
        return (timezone.now() + timedelta(days=3)).strftime("%m/%d/%Y - %H:%m")

    def _created(self):
        return (timezone.now() - timedelta(days=3)).strftime("%m/%d/%Y - %H:%m")

    def _amount(self):
        return f"{random.randrange(300, 1200):.4f}"

    def get_tickets(self, *args, **kwargs):
        return [
            {
                "seat": self._seat(),
                "ticket_number": self._ticket_number(),
                "ticket_id": self._ticket_id(),
                "company": self._company(),
                "trip": "New2",
                "origin": self._location(),
                "destination": self._location(),
                "departure": self._departure(),
                "amount": self._amount(),
                "payment_type": "EFEC",
                "created": self._created(),
                "is_open": None,
                "is_cancelled": None,
                "is_refunded": None,
                "refunded_on": None,
                "refunded_amount": None,
                "refunded_amount_total": "0.0000",
                "is_refundable": False,
                "retention_pct": 0,
            }
            for _ in range(2)
        ]

    def refund(self, *args, **kwargs):
        data = {
            "status": {"code": "0", "description": "Ok"},
            "details": {
                "refund_amount": "480",
                "boarding_tax": "0.00",
                "refund_amount_total": "480.00",
            },
        }

        return data
