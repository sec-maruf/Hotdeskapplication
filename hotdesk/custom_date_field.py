from django.db import models
import json

class DateArrayField(models.TextField):
    """A custom field to store an array of dates as a JSON string in the database."""

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return json.loads(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return None
        return json.loads(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        return json.dumps(value)
