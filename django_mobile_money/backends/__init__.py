from .wave import WaveBackend
from .orange_money import OrangeMoneyBackend
from .mtn_momo import MTNMoMoBackend
from .moov_money import MoovMoneyBackend

BACKENDS: dict = {
    "wave":         WaveBackend,
    "orange_money": OrangeMoneyBackend,
    "mtn_momo":     MTNMoMoBackend,
    "moov_money":   MoovMoneyBackend,
}

__all__ = [
    "BACKENDS",
    "WaveBackend",
    "OrangeMoneyBackend",
    "MTNMoMoBackend",
    "MoovMoneyBackend",
]