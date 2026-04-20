import json
import logging

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .backends import BACKENDS
from .exceptions import InvalidSignatureError, MobileMoneyError
from .models import WebhookLog
from .utils import update_transaction

logger = logging.getLogger("django_mobile_money")


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    """
    Vue générique pour recevoir les webhooks de tous les backends.

    Usage dans urls.py :
        path("webhooks/wave/", WebhookView.as_view(backend_id="wave")),
        path("webhooks/orange/", WebhookView.as_view(backend_id="orange_money")),
        path("webhooks/mtn/", WebhookView.as_view(backend_id="mtn_momo")),
        path("webhooks/moov/", WebhookView.as_view(backend_id="moov_money")),
    """
    backend_id: str = ""

    def post(self, request, *args, **kwargs):
        # Parse le payload
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        headers = dict(request.headers)

        # Log le webhook entrant
        log = WebhookLog.objects.create(
            backend=self.backend_id,
            payload=payload,
            headers=headers,
        )

        # Traite avec le bon backend
        try:
            backend_class = BACKENDS.get(self.backend_id)
            if not backend_class:
                raise MobileMoneyError(
                    backend=self.backend_id,
                    message=f"Backend '{self.backend_id}' introuvable",
                )

            backend = backend_class()
            result = backend.process_webhook(payload, headers)

            # Met à jour la transaction en base
            transaction = update_transaction(result["transaction_id"], result)

            # Met à jour le log
            log.processed = True
            log.transaction = transaction
            log.save()

            logger.info(
                "Webhook %s traité — transaction %s — statut %s",
                self.backend_id,
                result["transaction_id"],
                result["status"],
            )

            return HttpResponse(status=200)

        except InvalidSignatureError as exc:
            log.error = str(exc)
            log.save()
            logger.warning("Signature webhook invalide : %s", exc)
            return JsonResponse({"error": "Invalid signature"}, status=403)

        except MobileMoneyError as exc:
            log.error = str(exc)
            log.save()
            logger.error("Erreur webhook %s : %s", self.backend_id, exc)
            return JsonResponse({"error": str(exc)}, status=500)