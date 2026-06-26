import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator, model_validator


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(max_length=128)


class CreateUser(UserBase):
    password: SecretStr = Field(min_length=8, max_length=128)
    confirm_password: SecretStr = Field(min_length=8, max_length=128, exclude=True)

    @field_validator("full_name")
    @classmethod
    def check_fullname(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        if v.lower() in ["admin", "root"]:
            raise ValueError("Name is reserved")

        return v.title()

    @field_validator("password", "confirm_password", mode="before")
    @classmethod
    def strip_passwords(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("password", "confirm_password")
    @classmethod
    def check_password(cls, v: SecretStr) -> SecretStr:
        password_raw = v.get_secret_value()

        if not password_raw:
            raise ValueError("Password cannot be empty")
        if not re.search(r"\d", password_raw):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[A-Z]", password_raw):
            raise ValueError("Password must contain at least one uppercase letter")

        return v

    @model_validator(mode="after")
    def verify_password_match(self) -> "CreateUser":
        if self.password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("Passwords do not match")
        return self


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
