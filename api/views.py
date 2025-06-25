from collections import defaultdict
import calendar

from django.db.models import Sum, Q
from django.db.models.functions import ExtractMonth
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer
from .firebase_auth import FirebaseAuthentication, firebase_login_required


# 🚀 Main ViewSet for authenticated Firebase users
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(firebase_uid=self.request.user.username).order_by('-date')

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data.copy()
        data['firebase_uid'] = request.user.username
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'])
    def grouped(self, request):
        transactions = self.get_queryset()

        # Group by month
        by_month = defaultdict(lambda: {"income": 0, "expense": 0})
        for tx in transactions:
            month_key = tx.date.strftime('%Y-%m')
            by_month[month_key][tx.type] += float(tx.amount)

        # Group by category
        by_category = transactions.values('category').annotate(total=Sum('amount'))
        by_category_dict = {item['category']: float(item['total']) for item in by_category}

        return Response({
            "by_month": dict(by_month),
            "by_category": by_category_dict
        })


# 📊 Monthly income/expense totals
@api_view(['GET'])
@firebase_login_required
def monthly_report(request):
    firebase_uid = request.firebase_uid
    monthly_data = (
        Transaction.objects
        .filter(firebase_uid=firebase_uid)
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(
            income=Sum('amount', filter=Q(type='income')),
            expense=Sum('amount', filter=Q(type='expense'))
        )
        .order_by('month')
    )

    result = [
        {
            'month': calendar.month_abbr[entry['month']],
            'income': float(entry['income'] or 0),
            'expense': float(entry['expense'] or 0)
        }
        for entry in monthly_data
    ]

    return Response(result)


# 📈 Expense breakdown by category
@api_view(['GET'])
@firebase_login_required
def category_report(request):
    firebase_uid = request.firebase_uid
    category_data = (
        Transaction.objects
        .filter(firebase_uid=firebase_uid, type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    result = [
        {'category': item['category'], 'total': float(item['total'])}
        for item in category_data
    ]

    return Response(result)
