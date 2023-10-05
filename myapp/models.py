import random
import uuid

from django.db import models

# Create your models here.

def generate_unique_id():
    while True:
        # Generate a random integer between 100 and 999 (3 digits)
        user_id = random.randint(100, 999)
        # Check if the generated ID is unique
        if not customuser.objects.filter(pk=user_id).exists():
            return user_id

class customuser(models.Model):
    id = models.IntegerField(primary_key=True, default=generate_unique_id)
    username=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    creation_time=models.DateTimeField(auto_now_add=True)

class users_login(models.Model):
    id=models.AutoField(primary_key=True)
    user=models.ForeignKey(customuser, on_delete=models.CASCADE)
    login_time=models.DateTimeField(auto_now_add=True)

class subjectmark(models.Model):
    id=models.AutoField(primary_key=True)
    user_id = models.ForeignKey(customuser, on_delete=models.CASCADE, db_column='user_id')
    subject=models.CharField(max_length=100)
    marks_obtained=models.FloatField()
    total_marks=models.FloatField()
    score_date=models.DateField()
    percentage=models.FloatField(default=None)
