import mimetypes
from abc import abstractmethod
from enum import Enum, auto
from pathlib import Path
from typing import Any, Protocol
from uuid import UUID


class ObjectKind(Enum):
    PROFILE_AVATAR = auto()
    CHANNEL_AVATAR = auto()
    VIDEO = auto()
    VIDEO_PREVIEW = auto()
    CHANNEL_PREVIEW = auto()
    COURSE_PREVIEW = auto()


class KeyBuildingStrategy(Protocol):
    @abstractmethod
    def build_key(self, **context: Any) -> str: ...


_STRATEGY_REGISTRY: dict[ObjectKind, KeyBuildingStrategy] = {}


def register_strategy(object_kind: ObjectKind):
    def decorator(cls: type[KeyBuildingStrategy]):
        _STRATEGY_REGISTRY[object_kind] = cls()
        return cls
    return decorator


def _ext(fname: str) -> str:
    return Path(fname).suffix or mimetypes.guess_extension(
        mimetypes.guess_type(fname)[0] or ""
    ) or ".bin"


@register_strategy(ObjectKind.PROFILE_AVATAR)
class ProfileAvatarKeyStrategy(KeyBuildingStrategy):
    def build_key(self, *, source_filename: str, **_: Any) -> str:
        return f"other/user_avatar{_ext(source_filename)}"


@register_strategy(ObjectKind.CHANNEL_AVATAR)
class ChannelAvatarKeyStrategy(KeyBuildingStrategy):
    def build_key(self, *, channel_id: str, source_filename: str, **_: Any) -> str:
        return f"channels/{channel_id}/channel_avatar{_ext(source_filename)}"


@register_strategy(ObjectKind.CHANNEL_PREVIEW)
class ChannelPreviewKeyStrategy(KeyBuildingStrategy):
    def build_key(self, *, channel_id: str, source_filename: str, **_: Any) -> str:
        return f"channels/{channel_id}/channel_preview{_ext(source_filename)}"



@register_strategy(ObjectKind.VIDEO)
class VideoKeyStrategy(KeyBuildingStrategy):
    def build_key(self, *, channel_id: str, video_id: UUID, source_filename: str, **_: Any) -> str:
        return f"channels/{channel_id}/videos/{video_id}/video{_ext(source_filename)}"


@register_strategy(ObjectKind.VIDEO_PREVIEW)
class VideoPreviewKeyStrategy(KeyBuildingStrategy):
    def build_key(self, *, channel_id: str, video_id: UUID, source_filename: str, **_: Any) -> str:
        return f"channels/{channel_id}/videos/{video_id}/video_preview{_ext(source_filename)}"


def build_key(object_kind: ObjectKind, **context: Any) -> str:
    try:
        strategy = _STRATEGY_REGISTRY[object_kind]
    except KeyError as exc:
        raise ValueError(f"No strategy registered for {object_kind!r}") from exc
    return strategy.build_key(**context)

@register_strategy(ObjectKind.COURSE_PREVIEW)
class CoursePreviewKeyStrategy(KeyBuildingStrategy):
    def build_key(self, channel_id: str, course_id: str, source_filename: str, **_: Any) -> str:
        return f"channels/{channel_id}/courses/{course_id}/course_preview{_ext(source_filename)}"