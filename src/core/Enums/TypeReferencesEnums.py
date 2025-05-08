# src/core/enums/image_type.py
from __future__ import annotations

from enum import Enum
from typing import ClassVar, Dict, Final

from .ExtensionsEnums import ImageExtensionsEnum
from .MIMETypeEnums   import ImageMimeEnum


class InvalidUploadMimeError(ValueError):
    """Пользователь попытался загрузить неподдерживаемый MIME‑тип."""


class ImageTypeReferenceEnum(Enum):
    PNG  = (ImageExtensionsEnum.PNG , ImageMimeEnum.PNG )
    JPEG = (ImageExtensionsEnum.JPEG, ImageMimeEnum.JPEG)
    WEBP = (ImageExtensionsEnum.WEBP, ImageMimeEnum.WEBP)
    SVG  = (ImageExtensionsEnum.SVG , ImageMimeEnum.SVG )


    @property
    def ext(self)  -> ImageExtensionsEnum: return self.value[0]   
    @property
    def mime(self) -> ImageMimeEnum:      return self.value[1]   


    _EXT:  ClassVar[Dict[ImageExtensionsEnum, "ImageTypeReferenceEnum"]] = {}
    _MIME: ClassVar[Dict[ImageMimeEnum,      "ImageTypeReferenceEnum"]] = {}

    @classmethod
    def _init(cls) -> None:
        if not cls._EXT:        
            for it in cls:
                cls._EXT[it.ext]   = it
                cls._MIME[it.mime] = it


    @classmethod
    def from_ext(cls, ext: ImageExtensionsEnum | str) -> ImageExtensionsEnum:
        cls._init()
        if isinstance(ext, str):
            ext = ImageExtensionsEnum(ext.lower())
        try:
            return cls._EXT[ext].ext
        except KeyError:
            raise InvalidUploadMimeError(ext)

    @classmethod
    def from_mime(cls, mime: ImageMimeEnum | str) -> ImageExtensionsEnum:
        cls._init()
        if isinstance(mime, str):
            mime = ImageMimeEnum(mime.lower())
        try:
            return cls._MIME[mime].ext
        except KeyError:
            raise InvalidUploadMimeError(mime)
