from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLES = (
        ('participant', 'Participant'),
        ('expert', 'Expert'),
        ('admin', 'Admin'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES)
    organization = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Company(models.Model):
    SIZE_CHOICES = [
        ('Small', 'Small (1-50 employees)'),
        ('Medium', 'Medium (51-250 employees)'),
        ('Large', 'Large (251-1000 employees)'),
        ('Enterprise', 'Enterprise (1000+ employees)'),
    ]
    
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    location = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Audit(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expert_audits')
    participant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='participant_audits')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    framework = models.CharField(max_length=100, blank=True)
    objective = models.TextField(blank=True)
    completion = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"

class AuditQuestion(models.Model):
    STATUS_CHOICES = [
        ('not_answered', 'Not Answered'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partial', 'Partial'),
    ]
    
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='questions')
    category = models.CharField(max_length=100)
    question = models.TextField()
    response = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_answered')
    evidence = models.FileField(upload_to='audit_evidence/', blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.audit.name} - {self.question[:50]}"

class AuditHistory(models.Model):
    TYPE_CHOICES = [
        ('submission', 'Submission'),
        ('feedback', 'Feedback'),
        ('status_change', 'Status Change'),
    ]
    
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='history')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.audit.name} - {self.get_type_display()}"

class Report(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Report for {self.audit.name}"