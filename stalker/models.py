from django.db import models


class Purchase(models.Model):
    id = models.CharField(max_length=66, primary_key=True)
    state = models.CharField(max_length=40)


class Availability(models.Model):
    id = models.CharField(max_length=66, primary_key=True)
    freeSize = models.IntegerField()


class Slot(models.Model):
    id = models.CharField(max_length=66, primary_key=True)
    state = models.CharField(max_length=40)
