from pydantic import BaseModel
from typing import Literal, Optional, List

class NotifyRule(BaseModel):
    id: str
    queue_arn: str
    events: List[Literal["s3:ObjectCreated:*", "s3:ObjectCreated:Put"]] = ["s3:ObjectCreated:Put"]
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    def to_aws(self) -> dict:
        cfg = {"Id": self.id, "QueueArn": self.queue_arn, "Events": self.events}
        if self.prefix or self.suffix:
            cfg["Filter"] = {
                "Key": {"FilterRules": [
                    *([{"Name": "prefix", "Value": self.prefix}] if self.prefix else []),
                    *([{"Name": "suffix", "Value": self.suffix}] if self.suffix else []),
                ]}
            }
        return cfg



NOTIFY_RULES = [
    NotifyRule(id="user-avatar-png",  queue_arn="arn:minio:sqs::user_avatar:webhook", suffix="user_avatar.png"),
    NotifyRule(id="user-avatar-jpg",  queue_arn="arn:minio:sqs::user_avatar:webhook", suffix="user_avatar.jpg"),
    NotifyRule(id="user-avatar-jpeg", queue_arn="arn:minio:sqs::user_avatar:webhook", suffix="user_avatar.jpeg"),
    NotifyRule(id="user-avatar-webp", queue_arn="arn:minio:sqs::user_avatar:webhook", suffix="user_avatar.webp"),

    # channel avatar 
    NotifyRule(id="channel-avatar-png",  queue_arn="arn:minio:sqs::channel_avatar:webhook", suffix="channel_avatar.png"),
    NotifyRule(id="channel-avatar-jpg",  queue_arn="arn:minio:sqs::channel_avatar:webhook", suffix="channel_avatar.jpg"),
    NotifyRule(id="channel-avatar-jpeg", queue_arn="arn:minio:sqs::channel_avatar:webhook", suffix="channel_avatar.jpeg"),
    NotifyRule(id="channel-avatar-webp", queue_arn="arn:minio:sqs::channel_avatar:webhook", suffix="channel_avatar.webp"),

    # ---------- channel preview
    NotifyRule(id="channel-preview-png",  queue_arn="arn:minio:sqs::channel_preview:webhook", suffix="channel_preview.png"),
    NotifyRule(id="channel-preview-jpg",  queue_arn="arn:minio:sqs::channel_preview:webhook", suffix="channel_preview.jpg"),
    NotifyRule(id="channel-preview-jpeg", queue_arn="arn:minio:sqs::channel_preview:webhook", suffix="channel_preview.jpeg"),
    NotifyRule(id="channel-preview-webp", queue_arn="arn:minio:sqs::channel_preview:webhook", suffix="channel_preview.webp"),

    # video file 
    NotifyRule(id="video-upload", queue_arn="arn:minio:sqs::video:webhook", suffix="video"),

    # video preview 
    NotifyRule(id="video-preview-png",  queue_arn="arn:minio:sqs::video_preview:webhook", suffix="video_preview.png"),
    NotifyRule(id="video-preview-jpg",  queue_arn="arn:minio:sqs::video_preview:webhook", suffix="video_preview.jpg"),
    NotifyRule(id="video-preview-jpeg", queue_arn="arn:minio:sqs::video_preview:webhook", suffix="video_preview.jpeg"),
    NotifyRule(id="video-preview-webp", queue_arn="arn:minio:sqs::video_preview:webhook", suffix="video_preview.webp"),

    # course preview 
    NotifyRule(id="course-preview-png",  queue_arn="arn:minio:sqs::course_preview:webhook", suffix="course_preview.png"),
    NotifyRule(id="course-preview-jpg",  queue_arn="arn:minio:sqs::course_preview:webhook", suffix="course_preview.jpg"),
    NotifyRule(id="course-preview-jpeg", queue_arn="arn:minio:sqs::course_preview:webhook", suffix="course_preview.jpeg"),
    NotifyRule(id="course-preview-webp", queue_arn="arn:minio:sqs::course_preview:webhook", suffix="course_preview.webp"),
]