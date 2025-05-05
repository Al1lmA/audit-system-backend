from django.contrib import admin
from .models import User, Company, Audit, AuditQuestion, AuditHistory, Report

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Audit)
admin.site.register(AuditQuestion)
admin.site.register(AuditHistory)
admin.site.register(Report)