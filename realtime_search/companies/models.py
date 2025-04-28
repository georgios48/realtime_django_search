""" Company models """

from django.db import models


class Company(models.Model):
    """ Model representing a company """

    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    founded_year = models.IntegerField()

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return str(self.name)


class FinancialData(models.Model):
    """ Model representing financial data for a company """

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="financials")
    year = models.IntegerField()
    revenue = models.DecimalField(max_digits=15, decimal_places=2)
    net_income = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "Financial Data"
        verbose_name_plural = "Financial Data"

class CompanyDetails(models.Model):
    """ Model representing detailed information about a company """

    class CompanyType(models.TextChoices):
        """ CompanyType choices """

        PUBLIC = 'Public', 'Public'
        PRIVATE = 'Private', 'Private'

    class CompanySize(models.TextChoices):
        """ CompanySize choices """

        SMALL = 'Small', 'Small'
        MEDIUM = 'Medium', 'Medium'
        LARGE = 'Large', 'Large'

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="details")
    company_type = models.CharField(max_length=7, choices=CompanyType.choices)
    size = models.CharField(max_length=6, choices=CompanySize.choices)
    ceo_name = models.CharField(max_length=255)
    headquarters = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Company Details"
        verbose_name_plural = "Company Details"
