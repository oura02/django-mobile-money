from django.dispatch import Signal

payment_success = Signal()
payment_failed  = Signal()
payment_pending = Signal()