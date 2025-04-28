""" SearchConsumer tests """

# pylint: disable=protected-access

import json
import unittest
from unittest.mock import MagicMock

from channels.testing import WebsocketCommunicator
from django.test import TestCase

from . import exceptions as exc
from .consumers import SearchConsumer
from .models import Company, CompanyDetails, FinancialData


class SearchConsumerTests(TestCase):
    """Unit tests for the SearchConsumer WebSocket consumer"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up test data

        # Create company 1
        cls.company1 = Company.objects.create(
            name="Test Company",
            industry="Technology",
            country="USA",
            founded_year=2010
        )
        cls.company_details1 = CompanyDetails.objects.create(
            company=cls.company1,
            company_type="Public",
            size="Large",
            ceo_name="John Doe",
            headquarters="New York"
        )
        cls.financial_data1 = FinancialData.objects.create(
            company=cls.company1,
            year=2022,
            revenue=1000000.00,
            net_income=500000.00
        )

        # Create company 2
        cls.company2 = Company.objects.create(
            name="Another Corp",
            industry="Finance",
            country="Canada",
            founded_year=2015
        )
        cls.company_details2 = CompanyDetails.objects.create(
            company=cls.company2,
            company_type="Private",
            size="Medium",
            ceo_name="Jane Smith",
            headquarters="Toronto"
        )
        cls.financial_data1 = FinancialData.objects.create(
            company=cls.company1,
            year=2021,
            revenue=1000400.00,
            net_income=502000.00
        )

    @classmethod
    def tearDownClass(cls):
        # Clean up test data
        Company.objects.all().delete()
        super().tearDownClass()

    async def test_connect(self):
        """Test WebSocket connection is established properly"""

        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")

        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_disconnect(self):
        """Test WebSocket disconnect works properly"""

        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")

        await communicator.connect()
        await communicator.disconnect()
        # No assertion needed, just checking it completes without error

    async def test_receive_valid_query(self):
        """Test that a valid search query returns proper results"""

        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")

        await communicator.connect()

        # Send a valid search query
        await communicator.send_json_to({"query": "Technology"})

        # Get response
        response = await communicator.receive_json_from()

        # Verify response contains expected data
        self.assertIn("results", response)
        self.assertTrue(len(response["results"]) > 0)
        self.assertEqual(response["results"][0]["company_name"], "Test Company")
        self.assertEqual(response["results"][0]["industry"], "Technology")

        await communicator.disconnect()

    async def test_receive_short_query(self):
        """Test that a query with less than 3 characters returns an error"""

        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")

        await communicator.connect()

        # Send a too short query
        await communicator.send_json_to({"query": "Te"})

        # Get response
        response = await communicator.receive_json_from()

        # Verify response contains error
        self.assertIn("error", response)
        self.assertEqual(response["results"], [])

        await communicator.disconnect()


    async def test_receive_invalid_payload(self):
        """Test handling of invalid payload (non-string query)"""

        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")

        await communicator.connect()

        # Send query that is not a string
        await communicator.send_json_to({"query": 123})

        # Get response
        response = await communicator.receive_json_from()

        # Verify response contains error
        self.assertIn("error", response)
        self.assertEqual(response["results"], [])

        await communicator.disconnect()

    async def test_multiple_search_fields(self):
        """Test that search works across multiple fields"""

        communicator = WebsocketCommunicator(SearchConsumer.as_asgi(), "/ws/search/")

        await communicator.connect()

        # Search by company name
        await communicator.send_json_to({"query": "Test"})
        response1 = await communicator.receive_json_from()

        # Search by country
        await communicator.send_json_to({"query": "Canada"})
        response2 = await communicator.receive_json_from()

        # Search by CEO name
        await communicator.send_json_to({"query": "John"})
        response3 = await communicator.receive_json_from()

        # Verify all searches returned results
        self.assertTrue(len(response1["results"]) > 0)
        self.assertTrue(len(response2["results"]) > 0)
        self.assertTrue(len(response3["results"]) > 0)

        await communicator.disconnect()


class SearchConsumerHelperMethodTests(unittest.TestCase):
    """Tests for the helper methods in SearchConsumer"""

    def setUp(self):
        # Mock company object with details and financials
        self.company = MagicMock()
        self.company.name = "Test Company"
        self.company.industry = "Technology"
        self.company.country = "USA"

        self.company_details = MagicMock()
        self.company_details.company_type = "Public"
        self.company_details.size = "Large"
        self.company_details.ceo_name = "John Doe"
        self.company_details.headquarters = "New York"
        self.company.details = self.company_details

        financial1 = MagicMock()
        financial1.year = 2022
        financial1.revenue = 1000000.00
        financial1.net_income = 500000.00

        financial2 = MagicMock()
        financial2.year = 2021
        financial2.revenue = 800000.00
        financial2.net_income = 400000.00

        self.company.financials = MagicMock()
        self.company.financials.all.return_value = [financial1, financial2]
        self.company.financials.exists.return_value = True

    def test_extract_received_query_valid(self):
        """Test extracting a valid query"""

        text_data = json.dumps({"query": "Test Company"})
        result = SearchConsumer._extract_received_query(text_data)
        self.assertEqual(result, "Test Company")

        # Test stripping spaces
        text_data = json.dumps({"query": "  Test Company  "})
        result = SearchConsumer._extract_received_query(text_data)
        self.assertEqual(result, "Test Company")

    def test_extract_received_query_short(self):
        """Test extracting a query that's too short"""

        text_data = json.dumps({"query": "Te"})
        with self.assertRaises(exc.ShortQueryException):
            SearchConsumer._extract_received_query(text_data)

    def test_extract_received_query_invalid_type(self):
        """Test extracting a query that's not a string"""

        text_data = json.dumps({"query": 123})
        with self.assertRaises(exc.InvalidPayloadException):
            SearchConsumer._extract_received_query(text_data)

    def test_extract_received_query_invalid_json(self):
        """Test extracting from invalid JSON"""

        text_data = "{invalid json"
        with self.assertRaises(json.JSONDecodeError):
            SearchConsumer._extract_received_query(text_data)

    def test_enrich_search_results(self):
        """Test enriching search results with company data"""

        result = list(SearchConsumer._enrich_search_results(self.company))[0]

        self.assertEqual(result["company_name"], "Test Company")
        self.assertEqual(result["industry"], "Technology")
        self.assertEqual(result["country"], "USA")

        self.assertEqual(result["details"]["company_type"], "Public")
        self.assertEqual(result["details"]["size"], "Large")
        self.assertEqual(result["details"]["ceo_name"], "John Doe")
        self.assertEqual(result["details"]["headquarters"], "New York")

        self.assertEqual(len(result["financials"]), 2)
        self.assertEqual(result["financials"][0]["year"], 2022)
        self.assertEqual(result["financials"][0]["revenue"], 1000000.00)
        self.assertEqual(result["financials"][0]["net_income"], 500000.00)

    def test_enrich_search_results_no_details(self):
        """Test enriching search results when company has no details"""

        self.company.details = None
        result = list(SearchConsumer._enrich_search_results(self.company))[0]

        self.assertIsNone(result["details"])

    def test_enrich_search_results_no_financials(self):
        """Test enriching search results when company has no financials"""

        self.company.financials.exists.return_value = False
        result = list(SearchConsumer._enrich_search_results(self.company))[0]

        self.assertEqual(result["financials"], [])


    def test_build_search_fields(self):
        """Test building the list of fields to search across"""

        fields = SearchConsumer._build_search_fields()

        # Check that basic Company fields are included
        self.assertIn("name", fields)
        self.assertIn("country", fields)
        self.assertIn("industry", fields)
        self.assertIn("founded_year", fields)

        # Check that some relationship fields are included
        # (Can't test exact fields since we don't have models in this test class)
        self.assertTrue(any(field.startswith("details__") for field in fields))
        self.assertTrue(any(field.startswith("financials__") for field in fields))


if __name__ == "__main__":
    unittest.main()
