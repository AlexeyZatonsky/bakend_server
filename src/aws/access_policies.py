from enum import StrEnum, unique
from typing import Dict, Final




@unique
class AccessPolicy(StrEnum): 
    PRIVATE = "private"
    PUBLIC_READ = "public-read"
    AUTHENTICATED_READ = "authenticated-read"
    PUBLIC_READ_WRITE = "public-read-write"


ACL_HEADER: Final[str] = "x-amz-acl"


def header_for(policy: AccessPolicy) -> Dict[str, str]:
    return {ACL_HEADER: policy.value}