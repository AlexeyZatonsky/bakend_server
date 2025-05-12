from enum import StrEnum, unique
from typing import Dict, Final


@unique
class AccessPolicy(StrEnum):
    """
    Политики доступа к объектам в S3-хранилище.
    
    Определяет, кто и какие права имеет на доступ к объектам.
    Политики соответствуют стандартным настройкам ACL для S3.
    """
    PRIVATE = "private"
    PUBLIC_READ = "public-read"
    AUTHENTICATED_READ = "authenticated-read"
    PUBLIC_READ_WRITE = "public-read-write"


# Имя заголовка для передачи ACL-политики в запросах к S3
ACL_HEADER: Final[str] = "x-amz-acl"


def header_for(policy: AccessPolicy) -> Dict[str, str]:
    """
    Создает словарь заголовка для установки политики доступа.
    
    Args:
        policy: Политика доступа
        
    Returns:
        Dict[str, str]: Словарь с заголовком и значением политики
    """
    return {ACL_HEADER: policy.value}