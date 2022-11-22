from django.db import models


class Country(models.Model):
    class Continent(models.TextChoices):
        ASIA = 'asia', 'Asia'
        AFRICA = 'africa', 'Africa'
        EUROPE = 'europe', 'Europe'
        OCEANIA = 'oceania', 'Oceania'
        NORTH_AMERICA = 'north-america', 'North America'
        SOUTH_AMERICA = 'south-america', 'South America'
        ANTARCTICA = 'antarctica', 'Antarctica'

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=2)
    continent = models.CharField(max_length=13, choices=Continent.choices)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('name',)

    def __str__(self):
        return self.name
