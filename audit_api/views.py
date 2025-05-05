from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, Company, Audit, AuditQuestion, AuditHistory, Report
from .serializers import UserSerializer, CompanySerializer, AuditSerializer, ReportSerializer
from .permissions import IsAdminOrReadOnly, IsExpertOrAdmin, IsParticipantOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

class AuditViewSet(viewsets.ModelViewSet):
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'participant':
            return Audit.objects.filter(participant=user)
        elif user.role == 'expert':
            return Audit.objects.filter(expert=user)
        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def start_audit(self, request, pk=None):
        audit = self.get_object()
        if audit.status != 'planned':
            return Response({'error': 'Audit can only be started from planned status'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        audit.status = 'in_progress'
        audit.save()
        return Response({'status': 'Audit started'})

    @action(detail=True, methods=['post'])
    def complete_audit(self, request, pk=None):
        audit = self.get_object()
        if audit.status != 'in_progress':
            return Response({'error': 'Only audits in progress can be completed'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        audit.status = 'completed'
        audit.completion = 100
        audit.save()
        return Response({'status': 'Audit completed'})

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]