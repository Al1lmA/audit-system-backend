from rest_framework import serializers
from .models import User, Company, Audit, AuditQuestion, AuditHistory, Report
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'organization', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class AuditQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditQuestion
        fields = '__all__'

class AuditHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditHistory
        fields = '__all__'

class AuditSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    expert = UserSerializer(read_only=True)
    participant = UserSerializer(read_only=True)
    questions = AuditQuestionSerializer(many=True, read_only=True)
    history = AuditHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Audit
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'