from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'audits', AuditViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'interactions', InteractionViewSet)

urlpatterns = [
    path('users/login/', UserLoginView.as_view(), name='user-login'),
    path('csrf/', GetCSRFToken.as_view(), name='get-csrf-token'),
    # path('download/<path:filepath>', download_file, name='download-file'),
    # path('api/download/interaction/<str:filename>/', download_interaction_file,  name='download_interaction_file'),
    path('', include(router.urls)),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
