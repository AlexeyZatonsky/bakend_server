from __future__ import annotations

from enum import Enum
from typing import Dict, Final

from .ExtensionsEnums import ImageExtensionsEnum
from .MIMETypeEnums   import ImageMimeEnum


class InvalidUploadMimeError(ValueError):
    pass


class ImageTypeReferenceEnum(Enum):
    PNG  = (ImageExtensionsEnum.PNG , ImageMimeEnum.PNG )
    JPEG = (ImageExtensionsEnum.JPEG, ImageMimeEnum.JPEG)
    WEBP = (ImageExtensionsEnum.WEBP, ImageMimeEnum.WEBP)
    SVG  = (ImageExtensionsEnum.SVG , ImageMimeEnum.SVG )

    @property
    def ext(self)  -> ImageExtensionsEnum: return self.value[0]
    @property
    def mime(self) -> ImageMimeEnum:      return self.value[1]

    @classmethod
    def from_ext(cls, ext: ImageExtensionsEnum | str) -> ImageTypeReferenceEnum:
        if isinstance(ext, str):
            ext = ImageExtensionsEnum(ext.lower())
        try:
            return EXT_LOOKUP_BY_EXT[ext]
        except KeyError:
            raise InvalidUploadMimeError(ext)

    @classmethod
    def from_mime(cls, mime: ImageMimeEnum | str) -> ImageTypeReferenceEnum:
        if isinstance(mime, str):
            mime = ImageMimeEnum(mime.lower())
        try:
            return EXT_LOOKUP_BY_MIME[mime]
        except KeyError:
            raise InvalidUploadMimeError(mime)


EXT_LOOKUP_BY_EXT: Dict[ImageExtensionsEnum, ImageTypeReferenceEnum] = {
    item.ext: item for item in ImageTypeReferenceEnum
}
EXT_LOOKUP_BY_MIME: Dict[ImageMimeEnum, ImageTypeReferenceEnum] = {
    item.mime: item for item in ImageTypeReferenceEnum
}
