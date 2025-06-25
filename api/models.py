# models.py
from django.db import models

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    firebase_uid = models.CharField(max_length=128)  # store Firebase UID
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_recurring = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, blank=True, null=True)  # e.g. daily, weekly

    def __str__(self):
        return f"{self.title} - {self.amount}"
