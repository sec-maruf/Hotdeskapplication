# models.py
from django.db import models
class Desk(models.Model):
    desk_id = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    availability = models.BooleanField(default=True)
