import re
from typing import Any, Dict, Optional, Type

from config import PASSWORD_LENGTH
from errors import ApiError
from pydantic import BaseModel, EmailStr, ValidationError, validator

PASSWORD_REGEX_STR = (
    r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])"
    rf"(?=.*?[#?!@$%^&*-])*.{{{PASSWORD_LENGTH},}}$"
)
PASSWORD_REGEX = re.compile(PASSWORD_REGEX_STR)


class Register(BaseModel):
    email: EmailStr
    password: str

    @validator("password")
    def strong_password(cls, value: str):
        if not PASSWORD_REGEX.match(value):
            raise ValueError("password is to easy")
        return value


class Login(BaseModel):
    email: EmailStr
    password: str


class PatchUser(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]


class PostPatchAdvert(BaseModel):
    title: str
    description: str


SCHEMA_TYPE = (
    Type[Register] | Type[Login] | Type[PatchUser] | Type[PostPatchAdvert]
)


def validate(
    schema: SCHEMA_TYPE, data: Dict[str, Any], exclude_none: bool = True
) -> dict:
    try:
        validated = schema(**data).dict(exclude_none=exclude_none)
    except ValidationError as er:
        raise ApiError(400, er.errors())
    return validated
