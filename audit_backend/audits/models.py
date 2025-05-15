from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('expert', 'Expert'),
        ('participant', 'Participant'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    organization = models.ForeignKey('Company', null=True, blank=True, on_delete=models.SET_NULL)
    # status = models.CharField(max_length=20, default='active')
    last_login = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 

class Company(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    industry = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    # last_audit = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    @property
    def last_audit(self):
        last_audit = self.audits.order_by('-date').first()
        return last_audit.date if last_audit else None

class Audit(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    expert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expert_audits')
    score = models.PositiveIntegerField(null=True, blank=True)
    questionnaire_file = models.FileField(upload_to='questionnaires/', null=True, blank=True)
    participant_submission = models.FileField(upload_to='submissions/', null=True, blank=True)
    expert_feedback = models.TextField(blank=True)
    participant_feedback = models.TextField(blank=True)
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)

class Report(models.Model):
    audit = models.OneToOneField(Audit, on_delete=models.CASCADE)
    findings = models.TextField()
    recommendations = models.TextField()
    file = models.FileField(upload_to='final_reports/', null=True, blank=True)

class Interaction(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE)
    expert_comment = models.TextField(blank=True)
    participant_comment = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    files = models.FileField(upload_to='interactions/', null=True, blank=True)
