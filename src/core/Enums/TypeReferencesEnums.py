from __future__ import annotations

from enum import Enum
from typing import Dict, ClassVar
from pydantic import BaseModel

from .ExtensionsEnums import ImageExtensionsEnum
from .MIMETypeEnums import ImageMimeEnum


class InvalidUploadMimeError(ValueError):
    """Ошибка при недопустимом MIME-типе загружаемого файла."""
    pass


class ImageTypeReference(BaseModel):
    ext: ImageExtensionsEnum
    mime: ImageMimeEnum
    
    _by_ext: ClassVar[Dict[ImageExtensionsEnum, 'ImageTypeReference']] = {}
    _by_mime: ClassVar[Dict[ImageMimeEnum, 'ImageTypeReference']] = {}
    
    def model_post_init(self, __context) -> None:
        """Регистрируем экземпляр в словарях поиска при создании."""
        self.__class__._by_ext[self.ext] = self
        self.__class__._by_mime[self.mime] = self
    
    @classmethod
    def from_ext(cls, ext: str | ImageExtensionsEnum) -> 'ImageTypeReference':
        """Получить ссылку на тип по расширению файла."""
        if isinstance(ext, str):
            ext = ImageExtensionsEnum(ext.lower())
        try:
            return cls._by_ext[ext]
        except KeyError:
            raise InvalidUploadMimeError(f"Неподдерживаемое расширение файла: {ext}")
    
    @classmethod
    def from_mime(cls, mime: str | ImageMimeEnum) -> 'ImageTypeReference':
        """Получить ссылку на тип по MIME-типу."""
        if isinstance(mime, str):
            mime = ImageMimeEnum(mime.lower())
        try:
            return cls._by_mime[mime]
        except KeyError:
            raise InvalidUploadMimeError(f"Неподдерживаемый MIME-тип: {mime}")


PNG = ImageTypeReference(ext=ImageExtensionsEnum.PNG, mime=ImageMimeEnum.PNG)
JPEG = ImageTypeReference(ext=ImageExtensionsEnum.JPEG, mime=ImageMimeEnum.JPEG)
WEBP = ImageTypeReference(ext=ImageExtensionsEnum.WEBP, mime=ImageMimeEnum.WEBP)
SVG = ImageTypeReference(ext=ImageExtensionsEnum.SVG, mime=ImageMimeEnum.SVG)
