from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.db.models import IntegerField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey

class Diagnostic_test(models.Model):
    question_no = models.IntegerField()
    correct = models.IntegerField()
    probability = models.IntegerField()
    statement = models.CharField(max_length = 300)
    choice1 = models.CharField(max_length = 100)
    choice2 = models.CharField(max_length = 100)
    choice3 = models.CharField(max_length = 100)
    choice4 = models.CharField(max_length = 100)
    answer = models.CharField(max_length = 100)
    time = models.DateTimeField()
    