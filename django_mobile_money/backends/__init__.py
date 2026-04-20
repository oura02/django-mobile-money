from .wave import WaveBackend
from .orange_money import OrangeMoneyBackend
from .mtn_momo import MTNMoMoBackend
from .moov_money import MoovMoneyBackend
from .airtel_money import AirtelMoneyBackend
from .free_money import FreeMoneyBackend
from .mpesa import MPesaBackend
from .wizall_money import WizallMoneyBackend
from .celtiis_cash import CeltiisCashBackend
from .yas_money import YASMoneyBackend

BACKENDS: dict = {
    "wave":         WaveBackend,
    "orange_money": OrangeMoneyBackend,
    "mtn_momo":     MTNMoMoBackend,
    "moov_money":   MoovMoneyBackend,
    "airtel_money": AirtelMoneyBackend,
    "free_money":   FreeMoneyBackend,
    "mpesa":        MPesaBackend,
    "wizall_money": WizallMoneyBackend,
    "celtiis_cash": CeltiisCashBackend,
    "yas_money":    YASMoneyBackend,
}

__all__ = [
    "BACKENDS",
    "WaveBackend",
    "OrangeMoneyBackend",
    "MTNMoMoBackend",
    "MoovMoneyBackend",
    "AirtelMoneyBackend",
    "FreeMoneyBackend",
    "MPesaBackend",
    "WizallMoneyBackend",
    "CeltiisCashBackend",
    "YASMoneyBackend",
]