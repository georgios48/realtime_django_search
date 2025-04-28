""" Companies consumers """

import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q

from . import exceptions as exc
from .models import Company, CompanyDetails, FinancialData


class SearchConsumer(AsyncWebsocketConsumer):
    """ Live search functionality across Company and its related models """

    async def connect(self):
        """ Handshakes with the WebSocket """

        await self.accept()
        print("Handshaked with WebSocket successfully")

    async def disconnect(self, code):
        """ Closed connection with WebSocket """

        print(f"WebSocket connection closed with code: {code}")

    async def receive(self, text_data=None, bytes_data=None):
        """ Received message from WebSocket channel """

        # Try extracting received message
        try:
            query = SearchConsumer._extract_received_query(text_data)
        except (exc.ShortQueryException, exc.InvalidPayloadException) as e:
            await self.send(text_data=json.dumps(
                {
                    "error": e.message,
                    "results": []
                }
            ))
            return
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps(
                {
                    "error": "Invalid input format.",
                    "results": []
                }
            ))
            return

        # Perform search
        results = await self.search(query)

        # Send back the result of search
        await self.send(text_data=json.dumps(
            {"results": results}
            ))


    async def search(self, query):
        """ Perform search across Company and its related models """

        results = []

        search_conditions = SearchConsumer._build_search_conditions(query)

        # Get matching companies, avoiding duplicates
        companies = await SearchConsumer._get_companies(search_conditions)

        for company in companies:
            results.extend(SearchConsumer._enrich_search_results(company))

        return results


    # ! -------------- Helper methods -------------- ! #

    @staticmethod
    def _enrich_search_results(company: Company):
        """ Builds Json search result """

        yield ({
                "company_name": company.name,
                "industry": company.industry,
                "country": company.country,
                "details": {
                    "company_type": company.details.company_type if company.details.company_type else None,
                    "size": company.details.size if company.details.size else None,
                    "ceo_name": company.details.ceo_name if company.details.ceo_name else None,
                    "headquarters": company.details.headquarters if company.details.headquarters else None,
                } if company.details else None,
                "financials": [
                    {
                        "year": float(finance.year),
                        "revenue": float(finance.revenue),
                        "net_income": float(finance.net_income),
                    }
                    for finance in company.financials.all()
                ] if hasattr(company, "financials") and company.financials.exists() else []
            })

    @staticmethod
    def _extract_received_query(text_data):
        """
        Extracts received query from channel and strips its content, returns it.
        If query is empty or not a string -> raise error
        """

        data = json.loads(text_data).get("query", "")

        # Search only if user enters at least 3 characters, else raise short query exception
        if not isinstance(data, str):
            raise exc.InvalidPayloadException("Query must be a string")

        query = data.strip()

        if len(query) < 3:
            raise exc.ShortQueryException()

        return query

    @staticmethod
    def _build_search_fields():
        """
        Dynamically builds the list of fields to be searched across Company, CompanyDetails, and FinancialData
        """

        search_fields = ['name', 'country', 'industry', 'founded_year']

        # Add existing fields from CompanyDetails model
        for field in CompanyDetails._meta.get_fields():

            # Check only DB column fields and skip relationship fields
            if field.concrete and not field.is_relation:
                search_fields.append(f"details__{field.name}")

        # Add existing fields from FinancialData model
        for field in FinancialData._meta.get_fields():

            # Check only DB column fields and skip relationship fields
            if field.concrete and not field.is_relation:
                search_fields.append(f"financials__{field.name}")

        return search_fields

    @staticmethod
    def _build_search_conditions(query):
        """
        Build search conditions based on the fields of the model
        """

        search_fields = SearchConsumer._build_search_fields()

        search_conditions = Q()
        for field in search_fields:
            # Create new search conditions based on field
            search_conditions |= Q(**{f"{field}__icontains": query})

        return search_conditions

    @staticmethod
    @sync_to_async
    def _get_companies(search_conditions):
        """
        Get companies based on search conditions
        """

        return list(Company.objects.filter(search_conditions)\
            .distinct()\
                .select_related('details')\
                    .prefetch_related('financials'))
