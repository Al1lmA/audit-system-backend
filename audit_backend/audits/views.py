from django.shortcuts import render
from rest_framework import viewsets, permissions, status, parsers
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.middleware.csrf import get_token
# from django.views.decorators.csrf import csrf_exempt

class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({'csrfToken': get_token(request)})

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)  # username=email!
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'detail': 'Неверный email или пароль'}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in ['OPTIONS', 'POST']:
            return [AllowAny()]
        if self.request.method in ['DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdmin]

class AuditViewSet(viewsets.ModelViewSet):
    queryset = Audit.objects.all()
    # serializer_class = AuditSerializer
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AuditReadSerializer
        return AuditWriteSerializer
    permission_classes = [IsExpertOrAdmin]  # Только эксперт или админ
    
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
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def add_comment(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'comment added'})
        return Response(serializer.errors, status=400)

