from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.db import models

# Create your models here.
class MessageDetail(models.Model):
    message_id = models.CharField(max_length=100, primary_key=True)
    user_id = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    message_time = models.DateTimeField(auto_now_add=True)
    message_text = models.CharField(max_length=100)
    sticker_package_id = models.CharField(max_length=100, default=' ')
    sticker_id = models.CharField(max_length=100, default=' ')

    def __str__(self):
        return f'id:{self.message_id}\n{self.user_name}: {self.message_text}'

class Location(models.Model):
    message_id = models.CharField(max_length=100, primary_key=True)
    user_id = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    message_time = models.DateTimeField(auto_now_add=True)
    message_latitude = models.CharField(max_length=100)
    message_longitude = models.CharField(max_length=100)
    message_address = models.CharField(max_length=100)

    geometry = models.PointField(srid=4326, default=None)

    def __str__(self):
        return f'id:{self.message_id}\n{self.user_name}: {self.message_address}\n{self.message_latitude}, {self.message_longitude}'