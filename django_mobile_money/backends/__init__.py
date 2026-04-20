from .wave import WaveBackend
from .orange_money import OrangeMoneyBackend
from .mtn_momo import MTNMoMoBackend
from .moov_money import MoovMoneyBackend
from .airtel_money import AirtelMoneyBackend
from .free_money import FreeMoneyBackend
from .mpesa import MPesaBackend

BACKENDS: dict = {
    "wave":         WaveBackend,
    "orange_money": OrangeMoneyBackend,
    "mtn_momo":     MTNMoMoBackend,
    "moov_money":   MoovMoneyBackend,
    "airtel_money": AirtelMoneyBackend,
    "free_money":   FreeMoneyBackend,
    "mpesa":        MPesaBackend,
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
]