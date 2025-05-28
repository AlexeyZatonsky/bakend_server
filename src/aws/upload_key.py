from uuid import UUID
from pathlib import Path
from typing import Optional, Any

from pydantic import BaseModel, field_validator

from .strategies import ObjectKind, build_key


class UploadKey(BaseModel):
    user_id: UUID
    channel_id: Optional[str] = None
    video_id: Optional[UUID] = None
    course_id: Optional[UUID] = None

    kind: ObjectKind
    key: str
    ext: str

    @classmethod
    def from_context(
        cls,
        *,
        owner_id: UUID,
        kind: ObjectKind,
        source_filename: str,
        **context: Any,
    ) -> "UploadKey":
        key = build_key(kind, source_filename=source_filename, **context)
        ext = Path(source_filename).suffix.lstrip(".").lower()
        return cls(
            user_id=owner_id,
            kind=kind,
            key=key,
            ext=ext,
            channel_id=context.get("channel_id"),
            video_id=context.get("video_id"),
            course_id=context.get("course_id"),
        )

    @classmethod
    def from_s3(cls, *, user_id: UUID, key: str) -> Optional["UploadKey"]:
        parts = key.split("/")
        ext = Path(key).suffix.lstrip(".").lower()

        # user_avatar
        if parts == ["other", f"user_avatar.{ext}"]:
            return cls(user_id=user_id, kind=ObjectKind.PROFILE_AVATAR, key=key, ext=ext)

        # channels/{channel_id}/channel_avatar.*
        if len(parts) == 3 and parts[0] == "channels" and parts[2].startswith("channel_avatar"):
            return cls(user_id=user_id, channel_id=parts[1],
                       kind=ObjectKind.CHANNEL_AVATAR, key=key, ext=ext)

        # channels/{channel_id}/channel_preview.*
        if len(parts) == 3 and parts[0] == "channels" and parts[2].startswith("channel_preview"):
            return cls(user_id=user_id, channel_id=parts[1],
                       kind=ObjectKind.CHANNEL_PREVIEW, key=key, ext=ext)

        # channels/{channel_id}/videos/{video_id}/video*.*
        if len(parts) == 5 and parts[0] == "channels" and parts[2] == "videos":
            video_id = UUID(parts[3])
            if parts[4].startswith("video."):
                return cls(user_id=user_id, channel_id=parts[1],
                           video_id=video_id, kind=ObjectKind.VIDEO, key=key, ext=ext)
            if parts[4].startswith("video_preview"):
                return cls(user_id=user_id, channel_id=parts[1],
                           video_id=video_id, kind=ObjectKind.VIDEO_PREVIEW, key=key, ext=ext)

        # channels/{channel_id}/courses/{course_id}/course_preview.*
        if (len(parts) == 5 and parts[0] == "channels" and parts[2] == "courses"
                and parts[4].startswith("course_preview")):
            return cls(user_id=user_id, channel_id=parts[1],
                       course_id=UUID(parts[3]), kind=ObjectKind.COURSE_PREVIEW, key=key, ext=ext)

        return None

    @field_validator("ext")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()
