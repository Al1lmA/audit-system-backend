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
from django.http import FileResponse, Http404
import os
from django.conf import settings
from urllib.parse import unquote, quote
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser

@method_decorator(ensure_csrf_cookie, name='dispatch')
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
    
    @action(detail=True, methods=['post'], url_path='change_password')
    def change_password(self, request, pk=None):
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not user.check_password(old_password):
            return Response({'detail': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or len(new_password) < 6:
            return Response({'detail': 'New password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password changed successfully.'})

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

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
    parser_classes = [MultiPartParser, FormParser] # Добавьте парсеры

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def add_comment(self, request):
        # Обработка файлов
        files = request.FILES.getlist('files')
        
        # Создаем Interaction
        interaction = Interaction.objects.create(
            expert_comment=request.data.get('expert_comment'),
            audit_id=request.data.get('audit')
        )
        
        # Прикрепляем файлы
        for file in files:
            FileAttachment.objects.create(file=file, interaction=interaction)
        
        return Response({'status': 'comment added'})
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        audit = self.get_object()
        interactions = audit.interaction_set.order_by('date')
        
        # Добавьте логирование для отладки
        logger = logging.getLogger(__name__)
        
        serializer = InteractionSerializer(interactions, many=True)
        
        try:
            return Response(serializer.data)
        except ValueError as e:
            logger.error(f"Error serializing interactions: {str(e)}")
            # Возвращайте хотя бы базовые данные
            safe_data = []
            for interaction in interactions:
                safe_data.append({
                    'id': interaction.id,
                    'expert_comment': interaction.expert_comment,
                    'participant_comment': interaction.participant_comment,
                    'date': interaction.date,
                    'audit': interaction.audit_id,
                    'files': None  # Игнорируем проблемные файлы
                })
            return Response(safe_data)


def download_file(request, filepath):
    try:
        # Декодируем путь к файлу
        decoded_path = unquote(filepath)
        full_path = os.path.join(settings.MEDIA_ROOT, decoded_path)
        
        if not os.path.exists(full_path):
            raise Http404

        # Определяем имя файла и MIME-тип
        filename = os.path.basename(full_path)
        mime_type, _ = mimetypes.guess_type(full_path) or 'application/octet-stream'
        
        # Отправляем файл с правильными заголовками
        response = FileResponse(
            open(full_path, 'rb'),
            content_type=mime_type,
            as_attachment=True
        )
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'
        return response
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        raise Http404
    
def download_interaction_file(request, filename):
    try:
        # Декодируем имя файла из URL
        decoded_filename = unquote(filename)
        
        # Формируем абсолютный путь к файлу
        filepath = os.path.join(settings.MEDIA_ROOT, "interactions", decoded_filename)
        print(f"Путь к файлу: {filepath}")  # Для отладки
        
        if not os.path.exists(filepath):
            print(f"Файл не найден: {filepath}")
            raise Http404

        # Открываем файл и настраиваем ответ
        response = FileResponse(
            open(filepath, 'rb'),
            content_type='application/octet-stream',
            as_attachment=True,
            filename=decoded_filename  # Указываем оригинальное имя файла
        )
        return response
        
    except Exception as e:
        print(f"Ошибка скачивания: {str(e)}")
        raise Http404

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_companies = Company.objects.count()
        active_audits = Audit.objects.filter(status='In Progress').count()
        completed_audits = Audit.objects.filter(status='Completed').count()
        # Замените на свою логику для improvement_areas, если нужно
        improvement_areas = Audit.objects.filter(status='Improvement Needed').count() if hasattr(Audit, 'status') else 0

        return Response({
            "total_companies": total_companies,
            "active_audits": active_audits,
            "completed_audits": completed_audits,
            "improvement_areas": improvement_areas,
        })
    
class AuditViewSet(viewsets.ModelViewSet):
    queryset = Audit.objects.all()
    serializer_class = AuditReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        recent = self.request.query_params.get('recent')
        participant_id = self.request.query_params.get('participant')
        if participant_id:
            queryset = queryset.filter(participant_id=participant_id)
        if recent:
            queryset = queryset.order_by('-date')[:5]
        return queryset
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        audit = self.get_object()
        interactions = audit.interaction_set.order_by('date')
        from .serializers import InteractionSerializer
        serializer = InteractionSerializer(interactions, many=True)
        return Response(serializer.data)