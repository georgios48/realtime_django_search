from django.contrib import admin

from .models import Company, CompanyDetails, FinancialData


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "industry", "founded_year")

@admin.register(CompanyDetails)
class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ("company", "company_type", "size", "ceo_name", "headquarters")

@admin.register(FinancialData)
class FinancialDataAdmin(admin.ModelAdmin):
    list_display = ("company", "year", "revenue", "net_income")