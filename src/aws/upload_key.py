from uuid import UUID
from pathlib import Path
from typing import Optional, Any

from pydantic import BaseModel, field_validator

from .strategies import ObjectKind, build_key


class UploadKey(BaseModel):
    user_id: UUID
    channel_id: Optional[str] = None
    video_id: Optional[UUID] = None

    kind: ObjectKind
    key: str
    ext: str

    # ---------- helpers ----------
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
        )

    @classmethod
    def from_s3(cls, *, user_id: UUID, key: str) -> Optional["UploadKey"]:
        parts = key.split("/")
        ext = Path(key).suffix.lstrip(".").lower()

        # user avatar
        if parts == ["other", f"avatar.{ext}"]:
            return cls(user_id=user_id, kind=ObjectKind.PROFILE_AVATAR, key=key, ext=ext)

        # channel avatar
        if len(parts) == 3 and parts[0] == "channels" and parts[2].startswith("avatar"):
            return cls(user_id=user_id, channel_id=parts[1],
                       kind=ObjectKind.CHANNEL_AVATAR, key=key, ext=ext)

        # channels/{channel_id}/{video_id}/video.{ext}
        if (
            len(parts) == 4
            and parts[0] == "channels"
            and parts[3].startswith("video")
        ):
            return cls(user_id=user_id,
                       channel_id=parts[1],
                       video_id=UUID(parts[2]),
                       kind=ObjectKind.VIDEO,
                       key=key,
                       ext=ext)

        # channels/{channel_id}/{video_id}/preview.{ext}
        if (
            len(parts) == 4
            and parts[0] == "channels"
            and parts[3].startswith("preview")
        ):
            return cls(user_id=user_id,
                       channel_id=parts[1],
                       video_id=UUID(parts[2]),
                       kind=ObjectKind.VIDEO_PREVIEW,
                       key=key,
                       ext=ext)

        return None

    # ---------- validators ----------
    @field_validator("ext")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()
