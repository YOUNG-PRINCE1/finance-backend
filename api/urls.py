from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, monthly_report, category_report

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/monthly/', monthly_report, name='monthly-report'),
    path('reports/category/', category_report, name='category-report'),
]
