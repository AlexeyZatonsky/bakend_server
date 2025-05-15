from uuid import UUID
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, field_validator

from .strategies import ObjectKind, build_key




class UploadKey(BaseModel):
    user_id: UUID
    channel_id: Optional[str] = None
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
        **context: Any
    ) -> "UploadKey":
        key = build_key(kind, source_filename=source_filename, **context)
        ext = Path(source_filename).suffix.lstrip(".").lower()
        return cls(
            user_id=owner_id,
            kind=kind,
            key=key,
            ext=ext,
            channel_id=context.get("channel_id"),
            course_id=context.get("course_id"),
        )

    @classmethod
    def from_s3(cls, user_id: UUID, key: str) -> Optional["UploadKey"]:
        parts = key.split("/")
        ext = Path(key).suffix.lstrip(".").lower()

        if parts == ["other", f"avatar.{ext}"]:
            return cls(
                user_id=user_id,
                kind=ObjectKind.PROFILE_AVATAR,
                key=key,
                ext=ext
            )

        if len(parts) >= 3 and parts[2].startswith("avatar"):
            return cls(
                user_id=user_id,
                channel_id=parts[1],
                kind=ObjectKind.CHANNEL_AVATAR,
                key=key,
                ext=ext
            )

        if len(parts) >= 5 and parts[4].startswith("preview"):
            return cls(
                user_id=user_id,
                channel_id=UUID(parts[1]),
                course_id=UUID(parts[2]),
                kind=ObjectKind.COURSE_PREVIEW,
                key=key,
                ext=ext
            )

        return None

    @field_validator("ext")
    @classmethod
    def validate_ext(cls, v: str) -> str:
        return v.lower()

