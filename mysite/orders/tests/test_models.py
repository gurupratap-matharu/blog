import uuid
from unittest import skip

from django.conf import settings
from django.core import mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse_lazy

from faker import Faker
from trips.tests.utils import COMPLETE_SALE

from orders.factories import OrderFactory, PassengerFactory
from orders.models import Order, Passenger


fake = Faker()


class PassengerModelTests(TestCase):
    """
    Test suite for the passenger model.
    """

    def test_str_representation(self):
        passenger = PassengerFactory()
        self.assertEqual(str(passenger), f"{passenger.first_name}")

    def test_verbose_name_plural(self):
        passenger = PassengerFactory()

        self.assertEqual(str(passenger._meta.verbose_name), "passenger")
        self.assertEqual(
            str(passenger._meta.verbose_name_plural), "passengers"
        )

    def test_passenger_model_creation_is_accurate(self):
        # Arrange
        passenger = PassengerFactory()

        # Act
        passenger_from_db = Passenger.objects.first()

        # Assert
        self.assertEqual(Passenger.objects.count(), 1)
        self.assertEqual(
            passenger_from_db.document_type, passenger.document_type
        )
        self.assertEqual(
            passenger_from_db.document_number, passenger.document_number
        )
        self.assertEqual(passenger_from_db.first_name, passenger.first_name)
        self.assertEqual(passenger_from_db.last_name, passenger.last_name)
        self.assertEqual(passenger_from_db.nationality, passenger.nationality)
        self.assertEqual(passenger_from_db.gender, passenger.gender)
        self.assertEqual(passenger_from_db.birth_date, passenger.birth_date)
        self.assertEqual(
            passenger_from_db.phone_number, passenger.phone_number
        )

    def test_all_attributes_max_length(self):

        # Arrange
        _ = PassengerFactory()

        # Act
        passenger = Passenger.objects.first()

        def max_length(field_name):
            return passenger._meta.get_field(field_name).max_length

        doc_type_length = max_length("document_type")
        doc_num_length = max_length("document_number")
        first_name_length = max_length("first_name")
        last_name_length = max_length("last_name")
        gender_length = max_length("gender")
        phone_number_length = max_length("phone_number")

        # Assert
        self.assertEqual(doc_type_length, 10)
        self.assertEqual(doc_num_length, 50)
        self.assertEqual(first_name_length, 50)
        self.assertEqual(last_name_length, 50)
        self.assertEqual(gender_length, 1)
        self.assertEqual(phone_number_length, 17)

    def test_passengers_are_ordered_by_created_date(self):
        # Arrange
        p_1 = PassengerFactory()
        p_2 = PassengerFactory()
        p_3 = PassengerFactory()

        # Act
        passengers = Passenger.objects.all()

        # Assert
        self.assertEqual(passengers[0], p_3)
        self.assertEqual(passengers[1], p_2)
        self.assertEqual(passengers[2], p_1)

        passenger = passengers[0]
        ordering = passenger._meta.ordering[0]

        self.assertEqual(ordering, "-created_on")

    def test_passengers_are_indexed_by_created_date_descending(self):
        # Arrange
        p = PassengerFactory()

        # Act
        p.refresh_from_db()
        index = p._meta.indexes[0]

        # Assert
        self.assertEqual(index.fields, ["-created_on"])
        self.assertEqual(index.fields_orders, [("created_on", "DESC")])

    def test_passenger_get_full_name_method(self):
        p = PassengerFactory()

        actual = p.get_full_name()
        expected = f"{p.first_name} {p.last_name}"
        self.assertEqual(actual, expected)

    def test_passenger_dict_representation(self):
        p = PassengerFactory()

        actual = p.to_dict()
        expected = {
            "first_name": p.first_name,
            "last_name": p.last_name,
            "date_of_birth": p.birth_date.strftime("%Y-%m-%d"),
            "gender": p.gender,
            "document_type": p.document_type,
            "document_number": p.document_number,
            "nationality": p.nationality.code,
            "phone_number": p.phone_number,
        }

        self.assertEqual(actual, expected)


class OrderModelTests(TestCase):
    """
    Test suite for the Order Model.
    """

    def test_str_representation(self):
        order = OrderFactory()

        self.assertEqual(str(order), f"{order.name}")

    def test_verbose_name_plural(self):
        order = OrderFactory()

        self.assertEqual(str(order._meta.verbose_name), "order")
        self.assertEqual(str(order._meta.verbose_name_plural), "orders")

    def test_order_model_creation_is_accurate(self):
        # Arrange
        order = OrderFactory()

        # Act
        order_from_db = Order.objects.first()

        # Assert
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order_from_db.name, order.name)
        self.assertEqual(order_from_db.email, order.email)
        self.assertEqual(order_from_db.phone_number, order.phone_number)
        self.assertEqual(order_from_db.paid, order.paid)
        self.assertEqual(order_from_db.payment_id, order.payment_id)
        self.assertEqual(order_from_db.transaction_id, order.transaction_id)
        self.assertEqual(
            order_from_db.reservation_code, order.reservation_code
        )

    def test_all_attributes_max_length(self):
        # Arrange
        _ = OrderFactory()

        # Act
        order = Order.objects.first()

        name_max_length = order._meta.get_field("name").max_length
        phone_max_length = order._meta.get_field("phone_number").max_length
        payment_id_max_length = order._meta.get_field("payment_id").max_length
        transaction_id_max_length = order._meta.get_field(
            "transaction_id"
        ).max_length
        reservation_code_max_length = order._meta.get_field(
            "reservation_code"
        ).max_length

        # Assert
        self.assertEqual(name_max_length, 50)
        self.assertEqual(phone_max_length, 17)
        self.assertEqual(payment_id_max_length, 250)
        self.assertEqual(transaction_id_max_length, 50)
        self.assertEqual(reservation_code_max_length, 50)

    def test_new_order_is_always_unpaid(self):
        order = Order.objects.create(
            name="princy",
            email="princy@email.com",
            phone_number="+919999448805",
        )

        self.assertFalse(order.paid)
        self.assertEqual(order.payment_id, "")
        self.assertEqual(order.transaction_id, "")
        self.assertEqual(order.reservation_code, "")

    def test_orders_are_ordered_by_created_date(self):
        # Arrange
        Order.objects.all().delete()

        o_1 = OrderFactory()
        o_2 = OrderFactory()
        o_3 = OrderFactory()

        # Act

        orders = Order.objects.all()

        # Assert

        self.assertEqual(orders[0], o_3)
        self.assertEqual(orders[1], o_2)
        self.assertEqual(orders[2], o_1)

        order = orders[0]
        ordering = order._meta.ordering[0]

        self.assertEqual(ordering, "-created_on")

    @skip("Veer please implement get_absolute_url() on order")
    def test_order_absolute_url(self):
        order = OrderFactory()

        actual = order.get_absolute_url()
        expected = reverse_lazy("orders:order-detail", kwargs={"id": order.id})

        self.assertEqual(actual, expected)

    def test_order_cancel_url(self):
        order = OrderFactory()

        actual = order.get_cancel_url()
        expected = reverse_lazy("orders:order-cancel", kwargs={"id": order.id})

        self.assertEqual(actual, expected)

    def test_order_confirm_method_works(self):
        # Arrange
        order = OrderFactory(paid=False)

        guid = str(uuid.uuid4())
        payment_id = fake.bban()

        self.assertFalse(order.paid)

        # Act: confirm the order

        order.confirm(payment_id=payment_id, guid=guid)
        order.refresh_from_db()

        # Assert
        # 1. Order is marked as paid
        # 2. transaction_id, payment_id are set
        # 3. reservation_code is generated and set
        self.assertTrue(order.paid)
        self.assertEqual(order.transaction_id, guid)
        self.assertEqual(order.payment_id, payment_id)
        self.assertIsNotNone(order.reservation_code)
        self.assertEqual(len(order.reservation_code), 6)

    def test_order_cannot_be_confirmed_without_payment_id(self):
        # Arrange
        order = OrderFactory(paid=False)
        guid = str(uuid.uuid4())
        self.assertFalse(order.paid)

        # Act: try confirming the order without payment_id
        # this should raise ValidationError
        with self.assertRaises(ValidationError):
            order.confirm(payment_id=None, guid=guid)

    def test_order_cannot_be_confirmed_without_transaction_id(self):
        """
        Transaction_id is guid of API and its a uuid.
        """
        # Arrange
        order = OrderFactory(paid=False)
        payment_id = fake.bban()
        self.assertFalse(order.paid)

        # Act: try confirming the order without payment_id
        # this should raise ValidationError
        with self.assertRaises(ValidationError):
            order.confirm(payment_id=payment_id, guid=None)

    @skip("Should order confirmation be idempotent?")
    def test_order_confirmation_is_idempotent(self):
        self.fail("Not implemented yet")

    def test_order_send_user_email_method(self):
        # Arrange
        order = OrderFactory(paid=True)
        sale = COMPLETE_SALE

        context = sale
        context["order"] = order

        subject_path = "orders/emails/booking_confirmed_subject.txt"
        message_path = "orders/emails/booking_confirmed_message.txt"

        subject = render_to_string(subject_path, context).strip()
        message = render_to_string(message_path, context).strip()

        # Act
        order.send_user_email(sale=sale)

        # Assert
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, message)
        self.assertEqual(
            mail.outbox[0].from_email, settings.NOTIFICATION_EMAIL
        )
        self.assertEqual(mail.outbox[0].to, [order.email])
        self.assertEqual(mail.outbox[0].cc, [settings.NOTIFICATION_EMAIL])

    def test_order_send_confirmation_method(self):
        """This is a wrapper method that confirms and order and sends user
        a notification email"""

        # Arrange
        order = OrderFactory(paid=False)

        self.assertFalse(order.paid)
        self.assertEqual(order.payment_id, "")
        self.assertEqual(order.transaction_id, "")
        self.assertEqual(order.reservation_code, "")

        payment_id = fake.bban()
        guid = fake.uuid4()
        sale = COMPLETE_SALE

        # Act

        order.send_confirmation(payment_id, sale, guid)
        order.refresh_from_db()

        # Assert

        self.assertEqual(order.payment_id, payment_id)
        self.assertEqual(order.transaction_id, guid)
        self.assertIsNotNone(order.reservation_code)
        self.assertEqual(len(mail.outbox), 1)
