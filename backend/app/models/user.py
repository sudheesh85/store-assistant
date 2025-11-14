from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user model with common fields."""
    
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Remove spaces and special characters
            cleaned = "".join(c for c in v if c.isdigit())
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise ValueError("Mobile number must be 10-15 digits")
        return v

    def model_post_init(self, __context) -> None:
        """Validate that at least one of email or mobile is provided."""
        if not self.email and not self.mobile:
            raise ValueError("Either email or mobile must be provided")


class UserCreate(UserBase):
    """Model for user registration."""
    
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Model for user login."""
    
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    password: str = Field(..., min_length=1)

    def model_post_init(self, __context) -> None:
        """Validate that at least one of email or mobile is provided."""
        if not self.email and not self.mobile:
            raise ValueError("Either email or mobile must be provided")


class User(UserBase):
    """Full user model with all fields."""
    
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True


class UserInDB(User):
    """User model as stored in database."""
    
    password_hash: str


class AuthToken(BaseModel):
    """Authentication token response."""
    
    access_token: str
    token_type: str = "bearer"
    user: User


class AuthResponse(BaseModel):
    """Authentication response."""
    
    success: bool
    message: str
    data: Optional[AuthToken] = None
