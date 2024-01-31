# models.py
from django.db import models
class Desk(models.Model):
    desk_id = models.CharField(max_length=200)
    desk_description = models.CharField(max_length=200)
    capacity = models.IntegerField()
    #location = models.CharField(max_length=200)  # Can be used for specific location within a city
    country = models.CharField(max_length=100)  # New field for country
    city_name = models.CharField(max_length=100)  # New field for city name
    availability = models.BooleanField(default=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    post_code = models.CharField(max_length=5, default='00000')
    desk_number = models.IntegerField(default=0)
    ergonomic_chair_number = models.IntegerField(default=0)
    desk_monitor_number = models.IntegerField(default=0)
