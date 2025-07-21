from django.test import SimpleTestCase

from orders.forms import OrderForm, OrderSearchForm, PassengerForm


class OrderFormTests(SimpleTestCase):
    def test_form_is_invalid_for_empty_data(self):
        # Arrange
        data = dict()

        # Act
        form = OrderForm(data=data)

        # Assert

        error_msg = ["Este campo es necesario."]

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], error_msg)
        self.assertEqual(form.errors["phone_number"], error_msg)
        self.assertEqual(form.errors["email"], error_msg)
        self.assertEqual(form.errors["confirm_email"], error_msg)

    def test_form_is_valid_for_valid_data(self):
        data = {
            "name": "Gisela Vidal",
            "phone_number": "+5491112344321",
            "email": "gisela@email.com",
            "confirm_email": "gisela@email.com",
        }

        form = OrderForm(data=data)

        self.assertTrue(form.is_valid())

    def test_invalid_email_addreses_make_form_invalid(self):
        data = {
            "name": "Gisela Vidal",
            "phone_number": "+5491112344321",
            "email": "gisela@email.com",
            "confirm_email": "giselagv@email.com",  # emails do not match
        }

        form = OrderForm(data=data)

        actual = form.errors["confirm_email"][0]
        expected = OrderForm.INVALID_EMAIL_MSG

        self.assertFalse(form.is_valid())
        self.assertEqual(actual, expected)


class PassengerFormTests(SimpleTestCase):
    """
    Test suite for the passenger form.
    """

    def test_passenger_form_is_invalid_form_empty_data(self):
        data = dict()

        form = PassengerForm(data=data)
        error_msg = ["Este campo es necesario."]

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["document_type"], error_msg)
        self.assertEqual(form.errors["document_number"], error_msg)
        self.assertEqual(form.errors["nationality"], error_msg)
        self.assertEqual(form.errors["first_name"], error_msg)
        self.assertEqual(form.errors["last_name"], error_msg)
        self.assertEqual(form.errors["gender"], error_msg)
        self.assertEqual(form.errors["birth_date"], error_msg)
        self.assertEqual(form.errors["phone_number"], error_msg)


class OrderSearchFormTests(SimpleTestCase):
    """
    Test suite for order search form.
    """

    def test_on_valid_data(self):
        data = {"reservation_code": "ABC123", "email": "gisela@email.com"}

        form = OrderSearchForm(data=data)

        self.assertTrue(form.is_valid())

    def test_form_is_invalid_form_invalid_data(self):
        data_1 = dict(reservation_code="ABC123")
        data_2 = dict(email="gisela@email.com")
        error_msg = ["Este campo es necesario."]

        form_1 = OrderSearchForm(data=data_1)
        form_2 = OrderSearchForm(data=data_2)

        self.assertFalse(form_1.is_valid())
        self.assertFalse(form_2.is_valid())

        self.assertEqual(form_1.errors["email"], error_msg)
        self.assertEqual(form_2.errors["reservation_code"], error_msg)
