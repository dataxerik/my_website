from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
import datetime


@python_2_unicode_compatible
class Game(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    release_year = models.DateTimeField('game published date')
    developer = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)

    @property
    def is_released(self):
        if self.release_year <= timezone.now():
            return True
        return False

    def __str__(self):
        return "{0} was released in {1}".format(self.name, self.release_year)
