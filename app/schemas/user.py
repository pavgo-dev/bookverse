import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator, model_validator


def validate_password_strength(v: SecretStr) -> SecretStr:
    password_raw = v.get_secret_value()
    if not password_raw:
        raise ValueError("Password cannot be empty")
    if not re.search(r"\d", password_raw):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[A-Z]", password_raw):
        raise ValueError("Password must contain at least one uppercase letter")
    return v


def strip_raw_string(v: str) -> str:
    if isinstance(v, str):
        return v.strip()
    return v


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
        return strip_raw_string(v)

    @field_validator("password", "confirm_password")
    @classmethod
    def check_password(cls, v: SecretStr) -> SecretStr:
        return validate_password_strength(v)

    @model_validator(mode="after")
    def verify_password_match(self) -> "CreateUser":
        if self.password.get_secret_value() != self.confirm_password.get_secret_value():
            raise ValueError("Passwords do not match")
        return self


class UserProfileUpdate(BaseModel):
    email: EmailStr | None = Field(default=None)
    full_name: str | None = Field(default=None, max_length=128)

    @field_validator("full_name")
    @classmethod
    def check_fullname(cls, v: str | None) -> str | None:
        if v is None:
            return v
        else:
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty")
            if v.lower() in ["admin", "root"]:
                raise ValueError("Name is reserved")
            return v.title()


class UserPasswordUpdate(BaseModel):
    old_password: SecretStr = Field(min_length=8, max_length=128)
    new_password: SecretStr = Field(min_length=8, max_length=128)
    confirm_password: SecretStr = Field(min_length=8, max_length=128, exclude=True)

    @field_validator("old_password", "new_password", "confirm_password", mode="before")
    @classmethod
    def strip_passwords(cls, v: str) -> str:
        return strip_raw_string(v)

    @field_validator("new_password", "confirm_password")
    @classmethod
    def check_password(cls, v: SecretStr) -> SecretStr:
        return validate_password_strength(v)

    @model_validator(mode="after")
    def verify_password_match(self) -> "UserPasswordUpdate":
        old_raw = self.old_password.get_secret_value()
        new_raw = self.new_password.get_secret_value()
        confirm_raw = self.confirm_password.get_secret_value()

        if new_raw != confirm_raw:
            raise ValueError("Passwords do not match")
        if old_raw == new_raw:
            raise ValueError("New password cannot be the same as the old password")
        return self


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
