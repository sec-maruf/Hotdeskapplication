# models.py
from django.db import models
class Desk(models.Model):
    desk_id=models.CharField(max_length=200)
    desk_description= models.CharField(max_length=200)
    capacity = models.IntegerField()
    location = models.CharField(max_length=200)
    availability = models.BooleanField(default=True)
    start_time = models.DateTimeField()  # New field for start time
    end_time = models.DateTimeField()    # New field for end time
    price = models.DecimalField(max_digits=6, decimal_places=2)  # New field for price
    user_ratings = models.FloatField(default=0.0)  # New field for user ratings
    frequency_of_bookings = models.IntegerField(default=0)  # New field for frequency of bookings
    feedback = models.FloatField(default=0.0)  # New field for feedback
    accuracy_of_description = models.FloatField(default=0.0)  # New field for accuracy of description
