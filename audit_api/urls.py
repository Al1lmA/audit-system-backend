from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CompanyViewSet, AuditViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'audits', AuditViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = router.urls