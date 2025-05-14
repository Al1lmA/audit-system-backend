from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Company, Audit, Report, Interaction

# # Кастомная админка для пользователя
# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     list_display = ('username', 'email', 'role', 'organization', 'status', 'is_staff', 'last_login')
#     list_filter = ('role', 'status', 'is_staff', 'is_superuser')
#     search_fields = ('username', 'email', 'organization__name')
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('Дополнительно', {'fields': ('role', 'organization', 'status')}),
#     )
#     # Если organization - ForeignKey, используйте raw_id_fields для быстрого выбора
#     raw_id_fields = ('organization',)

# @admin.register(Company)
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ('name', 'contact_person', 'email', 'industry', 'size', 'location')
#     search_fields = ('name', 'contact_person', 'email', 'industry', 'location')

# @admin.register(Audit)
# class AuditAdmin(admin.ModelAdmin):
#     list_display = ('name', 'company', 'date', 'status', 'expert', 'score')
#     list_filter = ('status', 'date', 'company')
#     search_fields = ('name', 'company__name', 'expert__username')
#     raw_id_fields = ('company', 'expert')

# @admin.register(Report)
# class ReportAdmin(admin.ModelAdmin):
#     list_display = ('audit', 'findings', 'recommendations')
#     search_fields = ('audit__name', 'findings', 'recommendations')
#     raw_id_fields = ('audit',)

# @admin.register(Interaction)
# class InteractionAdmin(admin.ModelAdmin):
#     list_display = ('audit', 'date', 'expert_comment', 'participant_comment')
#     search_fields = ('audit__name', 'expert_comment', 'participant_comment')
#     raw_id_fields = ('audit',)

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Audit)
admin.site.register(Report)
admin.site.register(Interaction)
