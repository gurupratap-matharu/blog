from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core import mail
from django.test import TestCase

from lxml import etree
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from trips.providers.prosys import Prosys

from .utils import GET_BY_FECHA_ORIGEN_DESTINO_XML, START_SESSION_XML


class ProsysTests(TestCase):
    """
    Test suite for our custom interface which talks to prosys.
    """

    def test_class_attributes(self):
        """Test the class attributes are correctly set from settings."""

        self.assertEqual(Prosys.url, settings.CATA_WSDL)
        self.assertEqual(Prosys.user, settings.CATA_USER)
        self.assertEqual(Prosys.password, settings.CATA_PASSWORD)
        self.assertEqual(Prosys.web_id, settings.CATA_WEB_ID)
        self.assertEqual(Prosys.web_agency_id, settings.CATA_WEB_AGENCY_ID)
        self.assertEqual(Prosys.key, settings.CATA_KEY)

    @patch("trips.providers.prosys.Client")
    def test_init_without_connection_id(self, MockClient):
        # Arrange: set predefined conn_id
        connection_id = "43210"

        # Act: instantiate without connection_id
        with patch.object(
            Prosys, "start_session", return_value=connection_id
        ) as m_start_session:
            obj = Prosys()

        # Assert
        self.assertIsNotNone(obj.connection_id)
        self.assertEqual(obj.connection_id, connection_id)
        m_start_session.assert_called_once()

    @patch("trips.providers.prosys.Prosys.start_session")
    @patch("trips.providers.prosys.Client")
    def test_init_with_connection_id(self, MockClient, mock_start_session):
        # Arrange
        connection_id = "43215"

        # Act
        obj = Prosys(connection_id=connection_id)

        # Assert
        # verify connection_id is correctly set and new one is NOT generated
        self.assertEqual(obj.connection_id, connection_id)

        # verify start_session() was NOT called
        self.assertFalse(obj.start_session.called)
        obj.start_session.assert_not_called()

    @patch("trips.providers.prosys.Client", side_effect=ConnectionError)
    def test_init_with_connection_error(self, MockClient):
        # Arrange: Make the mock zeep client raise ConnectionError
        # see the `side_effect` keyword in the decorator

        # Act and assert

        with self.assertLogs("trips.providers.prosys", level="WARN") as cm:
            Prosys()

        self.assertEqual(len(mail.outbox), 1)
        self.assertGreaterEqual(len(cm.output), 1)

    @patch("trips.providers.prosys.Client", side_effect=Timeout)
    def test_init_with_timeout_error(self, MockClient):
        # Arrange: Make the mock zeep client raise Timeout
        # see the `side_effect` keyword in the decorator

        # Act and assert
        with self.assertLogs("trips.providers.prosys", level="WARN") as cm:
            Prosys()

        self.assertEqual(len(mail.outbox), 1)
        self.assertGreaterEqual(len(cm.output), 1)

    @patch("trips.providers.prosys.Client", side_effect=HTTPError)
    def test_init_with_http_error(self, MockClient):
        # Arrange: make the zeep client raise HTTP Error

        # Act and assert
        with self.assertLogs("trips.providers.prosys", level="WARN") as cm:
            Prosys()

        self.assertEqual(len(mail.outbox), 1)
        self.assertGreaterEqual(len(cm.output), 1)

    @patch("trips.providers.prosys.Client", side_effect=RequestException)
    def test_init_with_general_request_error(self, MockClient):
        # Arrange: make zeep client raise RequestException

        # Act and assert
        with self.assertLogs("trips.providers.prosys", level="WARN") as cm:
            Prosys()

        self.assertEqual(len(mail.outbox), 1)
        self.assertGreaterEqual(len(cm.output), 1)

    @patch("trips.providers.prosys.Client")
    def test_start_session_returns_connection_id(self, MockClient):
        # Arrange: build sample xml response for StartSession method
        expected = "554433"
        xml = START_SESSION_XML.format(connection_id=expected).encode()
        return_value = etree.fromstring(xml)

        client = MockClient()
        client.service.StartSession = MagicMock(return_value=return_value)

        # Act
        obj = Prosys()
        actual = obj.start_session()

        # Assert

        self.assertEqual(actual, expected)
        self.assertIsNotNone(obj.connection_id)
        self.assertEqual(obj.connection_id, actual)

    @patch("trips.providers.prosys.Client")
    def test_search_works_for_valid_arguments(self, MockClient):
        """THIS SHIT TEST DOESN'T WORK"""

        # Arrange: build sample xml response for GetByFechaOrigenDestino()

        xml = GET_BY_FECHA_ORIGEN_DESTINO_XML.encode()
        return_value = etree.fromstring(xml)

        client = MockClient()
        client.service.GetByFechaOrigenDestino = MagicMock(return_value=return_value)

        # Act

        obj = Prosys(connection_id="12345")
        actual = obj.search(origin="393", destination="443", departure="15-05-2025")
        print("veer actual: ", actual)

        # Assert
