import uuid
from django.db import models


class MobileTransaction(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        SUCCESS = "success", "Succès"
        FAILED  = "failed",  "Échoué"

    class Backend(models.TextChoices):
        WAVE         = "wave",         "Wave"
        ORANGE_MONEY = "orange_money", "Orange Money"
        MTN_MOMO     = "mtn_momo",     "MTN MoMo"
        MOOV_MONEY   = "moov_money",   "Moov Money"

    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id     = models.CharField(max_length=255, unique=True, db_index=True)
    provider_reference = models.CharField(max_length=255, blank=True)
    reference          = models.CharField(max_length=255, blank=True, db_index=True)
    backend            = models.CharField(max_length=20, choices=Backend.choices)
    phone              = models.CharField(max_length=20)
    amount             = models.DecimalField(max_digits=12, decimal_places=2)
    currency           = models.CharField(max_length=5, default="XOF")
    status             = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    message            = models.TextField(blank=True)
    raw_response       = models.JSONField(default=dict, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering         = ["-created_at"]
        verbose_name     = "Transaction Mobile Money"
        verbose_name_plural = "Transactions Mobile Money"
        indexes = [
            models.Index(fields=["backend", "status"]),
            models.Index(fields=["phone", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_backend_display()} | {self.phone} | {self.amount} {self.currency} | {self.get_status_display()}"

    @property
    def is_success(self):
        return self.status == self.Status.SUCCESS

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_failed(self):
        return self.status == self.Status.FAILED


class WebhookLog(models.Model):

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backend     = models.CharField(max_length=20)
    payload     = models.JSONField(default=dict)
    headers     = models.JSONField(default=dict)
    processed   = models.BooleanField(default=False)
    error       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(
        MobileTransaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="webhook_logs",
    )

    class Meta:
        ordering     = ["-created_at"]
        verbose_name = "Webhook Log"
        verbose_name_plural = "Webhook Logs"

    def __str__(self):
        return f"{self.backend} | {self.created_at:%Y-%m-%d %H:%M} | processed={self.processed}"