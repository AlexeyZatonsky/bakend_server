from enum import Enum

class MimeEnum(str, Enum): pass


class ImageMimeEnum(MimeEnum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    WEBP = "image/webp"
    SVG = "image/svg+xml"