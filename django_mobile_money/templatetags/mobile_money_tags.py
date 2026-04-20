from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def payment_button(phone, amount, backend="wave", label="Payer maintenant", css_class="btn-pay"):
    """
    Tag template pour afficher un bouton de paiement.

    Usage dans un template :
        {% load mobile_money_tags %}
        {% payment_button phone="+22507XXXXXXXX" amount=5000 backend="wave" %}
    """
    colors = {
        "wave": "#1A73E8",
        "orange_money": "#FF6600",
        "mtn_momo": "#FFCC00",
        "moov_money": "#0066CC",
    }
    color = colors.get(backend, "#1A73E8")

    return format_html(
        '''<button
            class="{css_class}"
            data-backend="{backend}"
            data-phone="{phone}"
            data-amount="{amount}"
            style="background:{color};color:white;padding:10px 20px;
                   border:none;border-radius:6px;cursor:pointer;font-size:14px">
            {label}
        </button>''',
        css_class=css_class,
        backend=backend,
        phone=phone,
        amount=amount,
        color=color,
        label=label,
    )


@register.simple_tag
def transaction_status_badge(status):
    """
    Affiche un badge coloré pour le statut d'une transaction.

    Usage :
        {% load mobile_money_tags %}
        {% transaction_status_badge transaction.status %}
    """
    config = {
        "success": ("#28a745", "Succès"),
        "pending": ("#ffc107", "En attente"),
        "failed": ("#dc3545", "Échoué"),
    }
    color, label = config.get(status, ("#6c757d", status))

    return format_html(
        '<span style="background:{};color:white;padding:3px 10px;'
        'border-radius:12px;font-size:12px">{}</span>',
        color,
        label,
    )