from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import re

# --- USER SCHEMAS ---

class UserBase(BaseModel):
    # Regex Breakdown:
    # ^[a-zA-Z]      -> Must start with an alphabet (upper or lower)
    # [^\s]*         -> Followed by zero or more characters that are NOT whitespace (allows special chars)
    # $              -> End of string
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        pattern=r"^[a-zA-Z][^\s]*$", 
        description="Starts with an alphabet, no spaces allowed, special characters permitted."
    )
    email: EmailStr = Field(..., description="Must be a valid email format (e.g., user@example.com)")

class UserCreate(UserBase):
    # Validates password length (at least 8 characters)
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="Password must be at least 8 characters long"
    )

    # Optional: Add a custom validator if you want to ensure the password isn't just spaces
    @field_validator('password')
    @classmethod
    def password_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError('Password cannot contain spaces')
        return v

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- AUTH/TOKEN SCHEMAS ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None