from pydantic import BaseModel, Field
from typing import Literal, Optional, List


class NotifyRule(BaseModel):
    id: str
    queue_arn: str
    events: List[Literal["s3:ObjectCreated:*", "s3:ObjectCreated:Put"]] = ["s3:ObjectCreated:Put"]
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    def to_aws(self) -> dict:
        cfg = {
            "Id": self.id,
            "QueueArn": self.queue_arn,
            "Events": self.events,
        }
        if self.prefix or self.suffix:
            cfg["Filter"] = {
                "Key": {"FilterRules": [
                    *([{"Name": "prefix", "Value": self.prefix}] if self.prefix else []),
                    *([{"Name": "suffix", "Value": self.suffix}] if self.suffix else []),
                ]}
            }
        return cfg


NOTIFY_RULES = [
    # ─── аватары ───────────────────────────────────────────────────────────────
    NotifyRule(id="user-avatar",    queue_arn="arn:minio:sqs::user_avatar:webhook",    prefix="other/avatar"),
    NotifyRule(id="channel-avatar", queue_arn="arn:minio:sqs::channel_avatar:webhook", prefix="channels/"),

    # ─── видео ────────────────────────────────────────────────────────────────
    NotifyRule(id="video-upload",         queue_arn="arn:minio:sqs::video:webhook",          prefix="videos/", suffix="video"),
    NotifyRule(id="video-preview-upload", queue_arn="arn:minio:sqs::video_preview:webhook",  prefix="videos/", suffix="preview"),
]
