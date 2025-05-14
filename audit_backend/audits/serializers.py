from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'organization', 'status', 'last_login']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class AuditWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = '__all__'

class AuditReadSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    expert = UserSerializer(read_only=True)

    class Meta:
        model = Audit
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'
