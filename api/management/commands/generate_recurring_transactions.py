from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from api.models import Transaction  

class Command(BaseCommand):
    help = "Generate new transactions for recurring entries"

    def handle(self, *args, **kwargs):
        today = now().date()
        recurring = Transaction.objects.filter(is_recurring=True)

        created = 0

        for tx in recurring:
            # Find the most recent matching transaction by firebase_uid, title, and frequency
            last_tx = Transaction.objects.filter(
                firebase_uid=tx.firebase_uid,
                title=tx.title,
                amount=tx.amount,
                category=tx.category,
                type=tx.type,
                is_recurring=True,
                frequency=tx.frequency,
            ).order_by('-date').first()

            # If never duplicated, or due for next one
            if not last_tx:
                continue

            delta_days = (today - last_tx.date).days
            should_create = (
                (tx.frequency == "daily" and delta_days >= 1) or
                (tx.frequency == "weekly" and delta_days >= 7) or
                (tx.frequency == "monthly" and delta_days >= 30)
            )

            if should_create:
                Transaction.objects.create(
                    firebase_uid=tx.firebase_uid,
                    title=tx.title,
                    amount=tx.amount,
                    category=tx.category,
                    type=tx.type,
                    is_recurring=True,
                    frequency=tx.frequency,
                    date=today,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created {created} recurring transactions"))
