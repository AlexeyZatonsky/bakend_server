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


    _EXT_MAP:  ClassVar[Dict[ImageExtensionsEnum, "ImageTypeReferenceEnum"]]
    _MIME_MAP: ClassVar[Dict[ImageMimeEnum,      "ImageTypeReferenceEnum"]]

    @classmethod
    def _init_maps(cls) -> None:
        if not hasattr(cls, "_EXT_MAP"):           
            cls._EXT_MAP  = {it.ext : it for it in cls}
            cls._MIME_MAP = {it.mime: it for it in cls}


    @classmethod
    def from_ext(cls, ext: ImageExtensionsEnum | str) -> "ImageTypeReferenceEnum":
        """
        Принимает либо Enum, либо «png» и возвращает ImageTypeReferenceEnum.
        """
        cls._init_maps()

        if isinstance(ext, str):
            try:
                ext = ImageExtensionsEnum(ext.lower())
            except ValueError as exc:               
                raise InvalidUploadMimeError(ext) from exc

        try:
            return cls._EXT_MAP[ext]               
        except KeyError as exc:
            raise InvalidUploadMimeError(ext.value) from exc
        

    @classmethod
    def from_mime(cls, mime: ImageMimeEnum | str) -> "ImageTypeReferenceEnum":
        """
        Принимает Enum или строку «image/png».
        """
        cls._init_maps()

        if isinstance(mime, str):
            try:
                mime = ImageMimeEnum(mime.lower())
            except ValueError as exc:
                raise InvalidUploadMimeError(mime) from exc

        try:
            return cls._MIME_MAP[mime]
        except KeyError as exc:
            raise InvalidUploadMimeError(mime.value) from exc
