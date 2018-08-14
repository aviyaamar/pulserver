import enum
from django.utils.timezone import now

from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    email = models.CharField(max_length=255)
    company_name = models.CharField(max_length=30)
    user_name = models.CharField(max_length=30)
    user_password = models.CharField(max_length=30)
    auth_key = models.TextField()

class Computers(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    auth_key = models.TextField()
    version = models.TextField(null=True, blank=True)
    computer_name = models.TextField(null=True, blank=True)
    operating_system = models.TextField(null=True, blank=True)
    cpu = models.TextField(null=True, blank=True)
    memory = models.TextField(null=True, blank=True)
    upgrade_in_progress = models.BooleanField(default=False)

class Statistics(models.Model):
    computer = models.ForeignKey(Computers, on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=now)
    time_received = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30)
    content = models.TextField()

class Logs(models.Model):
    time_created = models.DateTimeField(default=now)
    text_content = models.TextField()
    path = models.TextField()
    computer = models.ForeignKey(Computers, on_delete=models.CASCADE)
    log_type = models.TextField()
    time_received = models.DateTimeField(auto_now_add=True)
    process = models.BooleanField()

class Command(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    computer = models.ForeignKey(Computers, on_delete=models.CASCADE)
    time_execution = models.DateTimeField(auto_now_add=True)
    command = models.TextField()
    outcome = models.TextField(blank=True, null=True)
    errors = models.BooleanField()
    sent = models.BooleanField()
    completed = models.BooleanField()

class Alerts(models.Model):
    time_received = models.DateTimeField(auto_now_add=True)
    computer = models.ForeignKey(Computers, on_delete=models.CASCADE)
    key = models.TextField(blank=True, null=True)
    severity_level = models.TextField()
    alert_description = models.TextField()
    read_by_user = models.BooleanField()

class Software(models.Model):
    computer = models.ForeignKey(Computers, on_delete=models.CASCADE)
    name = models.TextField()
    current_version = models.TextField()
    upgrade_version = models.TextField(blank=True, null=True)
