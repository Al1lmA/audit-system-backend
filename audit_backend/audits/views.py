from django.shortcuts import render
from rest_framework import viewsets, permissions, status, parsers
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class AuditViewSet(viewsets.ModelViewSet):
    queryset = Audit.objects.all()
    # serializer_class = AuditSerializer
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AuditReadSerializer
        return AuditWriteSerializer
    
    @action(detail=True, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def upload_questionnaire(self, request, pk=None):
        audit = self.get_object()
        file = request.FILES.get('questionnaire_file')
        if file:
            audit.questionnaire_file = file
            audit.save()
            return Response({'status': 'questionnaire uploaded'})
        return Response({'error': 'No file provided'}, status=400)

    @action(detail=True, methods=['get'])
    def download_questionnaire(self, request, pk=None):
        audit = self.get_object()
        if audit.questionnaire_file:
            return Response({'url': audit.questionnaire_file.url})
        return Response({'error': 'No questionnaire uploaded'}, status=404)

    @action(detail=True, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def upload_participant_submission(self, request, pk=None):
        audit = self.get_object()
        file = request.FILES.get('participant_submission')
        if file:
            audit.participant_submission = file
            audit.save()
            return Response({'status': 'submission uploaded'})
        return Response({'error': 'No file provided'}, status=400)

    @action(detail=True, methods=['get'])
    def download_participant_submission(self, request, pk=None):
        audit = self.get_object()
        if audit.participant_submission:
            return Response({'url': audit.participant_submission.url})
        return Response({'error': 'No submission uploaded'}, status=404)

    @action(detail=True, methods=['get'])
    def download_report(self, request, pk=None):
        audit = self.get_object()
        if audit.report_file:
            return Response({'url': audit.report_file.url})
        return Response({'error': 'No report uploaded'}, status=404)
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        audit = self.get_object()
        interactions = audit.interaction_set.order_by('date')
        serializer = InteractionSerializer(interactions, many=True)
        return Response(serializer.data)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer

    @action(detail=False, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def add_comment(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'comment added'})
        return Response(serializer.errors, status=400)

