from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'organization', 'phone']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'participant'),
            organization=validated_data.get('organization'),
            phone=validated_data.get('phone', '')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'organization', 'phone', 'password', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}, # required=False!
            'phone': {'required': False} 
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

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
        fields = ['id', 'expert_comment', 'participant_comment', 'date', 'files', 'audit']
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Проверка на существование файла
        if not instance.files or not instance.files.name:
            ret['files'] = None
        return ret