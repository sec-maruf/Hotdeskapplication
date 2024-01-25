from django.db import models
from hotdesk.models import Desk

class Booking(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='bookings')
    user = models.CharField(max_length=100)  # Replace with ForeignKey to User if applicable
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.desk.desk_id}"

