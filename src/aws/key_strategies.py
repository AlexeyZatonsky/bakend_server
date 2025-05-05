import mimetypes
from abc import abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import Any, Protocol
from uuid import UUID





class ObjectKind(Enum):
    """Поддерживаемые типы объектов, для которых формируем ключи."""

    PROFILE_AVATAR = auto()
    CHANNEL_AVATAR = auto()
    VIDEO = auto()


class KeyBuildingStrategy(Protocol):
    """Контракт, которому должны соответствовать все стратегии."""

    @abstractmethod
    def build_key(self, **context: Any) -> str:  
        """Сформировать и вернуть S3‑ключ на основании контекста."""
        ...


# Глобальный реестр стратегий: ObjectKind → стратегия‑singleton
_STRATEGY_REGISTRY: dict[ObjectKind, KeyBuildingStrategy] = {}


def register_strategy(object_kind: ObjectKind):
    """Декоратор: регистрирует класс‑стратегию в реестре."""

    def decorator(strategy_cls: type[KeyBuildingStrategy]):
        _STRATEGY_REGISTRY[object_kind] = strategy_cls()
        return strategy_cls

    return decorator



@register_strategy(ObjectKind.PROFILE_AVATAR)
class ProfileAvatarKeyStrategy(KeyBuildingStrategy):
    """`other/avatar.<ext>` — ключ аватара пользователя."""

    def build_key(self, *, source_filename: str, **_: Any) -> str:  
        extension: str = (
            Path(source_filename).suffix
            or mimetypes.guess_extension(mimetypes.guess_type(source_filename)[0] or "")
            or ".bin"
        )
        return f"other/avatar{extension}"


@register_strategy(ObjectKind.CHANNEL_AVATAR)
class ChannelAvatarKeyStrategy(KeyBuildingStrategy):
    """`channels/{channel_id}/avatar.<ext>` — ключ аватара канала."""

    def build_key(self, *, channel_id: UUID, source_filename: str, **_: Any) -> str:  
        extension: str = (
            Path(source_filename).suffix
            or mimetypes.guess_extension(mimetypes.guess_type(source_filename)[0] or "")
            or ".bin"
        )
        return f"channels/{channel_id}/avatar{extension}"


@register_strategy(ObjectKind.VIDEO)
class VideoKeyStrategy(KeyBuildingStrategy):
    """`channels/{channel_id}/videos/{video_id}<ext>` — ключ видеоматериала."""

    def build_key(
        self,
        *,
        channel_id: UUID,
        video_id: UUID,
        source_filename: str,
        **_: Any,
    ) -> str:  
        extension: str = (
            Path(source_filename).suffix
            or mimetypes.guess_extension(mimetypes.guess_type(source_filename)[0] or "")
            or ".bin"
        )
        return f"channels/{channel_id}/videos/{video_id}{extension}"