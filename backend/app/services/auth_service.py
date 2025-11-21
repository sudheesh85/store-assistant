from __future__ import annotations

import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import bcrypt

from app.core.settings import settings
from app.models.user import User, UserCreate, UserInDB, UserLogin


class AuthService:
    """Service for user authentication and management."""

    def __init__(self):
        self.users_file = settings.DATA_STORAGE_PATH / "users.json"
        self.tokens_file = settings.DATA_STORAGE_PATH / "tokens.json"
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self):
        """Ensure users and tokens files exist."""
        if not self.users_file.exists():
            self.users_file.write_text("{}")
        if not self.tokens_file.exists():
            self.tokens_file.write_text("{}")

    def _load_users(self) -> dict[str, UserInDB]:
        """Load users from file."""
        try:
            data = json.loads(self.users_file.read_text())
            return {
                user_id: UserInDB(**user_data)
                for user_id, user_data in data.items()
            }
        except Exception:
            return {}

    def _save_users(self, users: dict[str, UserInDB]):
        """Save users to file."""
        data = {
            user_id: user.model_dump(mode="json")
            for user_id, user in users.items()
        }
        self.users_file.write_text(json.dumps(data, indent=2, default=str))

    def _load_tokens(self) -> dict[str, dict]:
        """Load tokens from file."""
        try:
            return json.loads(self.tokens_file.read_text())
        except Exception:
            return {}

    def _save_tokens(self, tokens: dict[str, dict]):
        """Save tokens to file."""
        self.tokens_file.write_text(json.dumps(tokens, indent=2, default=str))

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def _generate_token(self) -> str:
        """Generate a random access token."""
        return secrets.token_urlsafe(32)

    def _find_user_by_email(self, email: str) -> Optional[tuple[str, UserInDB]]:
        """Find user by email."""
        users = self._load_users()
        for user_id, user in users.items():
            if user.email and user.email.lower() == email.lower():
                return user_id, user
        return None

    def _find_user_by_mobile(self, mobile: str) -> Optional[tuple[str, UserInDB]]:
        """Find user by mobile."""
        users = self._load_users()
        # Clean the mobile number for comparison
        cleaned_mobile = "".join(c for c in mobile if c.isdigit())
        for user_id, user in users.items():
            if user.mobile:
                cleaned_user_mobile = "".join(c for c in user.mobile if c.isdigit())
                if cleaned_user_mobile == cleaned_mobile:
                    return user_id, user
        return None

    def register(self, user_create: UserCreate) -> tuple[User, str]:
        """
        Register a new user.
        
        Returns:
            Tuple of (User, access_token)
        
        Raises:
            ValueError: If user already exists
        """
        # Check if user already exists
        if user_create.email:
            existing = self._find_user_by_email(user_create.email)
            if existing:
                raise ValueError("User with this email already exists")
        
        if user_create.mobile:
            existing = self._find_user_by_mobile(user_create.mobile)
            if existing:
                raise ValueError("User with this mobile number already exists")

        # Create new user
        user_id = secrets.token_urlsafe(16)
        password_hash = self._hash_password(user_create.password)
        
        now = datetime.utcnow()
        user_in_db = UserInDB(
            id=user_id,
            email=user_create.email,
            mobile=user_create.mobile,
            name=user_create.name,
            password_hash=password_hash,
            created_at=now,
            last_login=now,
            is_active=True,
        )

        # Save user
        users = self._load_users()
        users[user_id] = user_in_db
        self._save_users(users)

        # Generate and save token
        token = self._generate_token()
        tokens = self._load_tokens()
        tokens[token] = {
            "user_id": user_id,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=7)).isoformat()
        }
        self._save_tokens(tokens)

        # Return user without password hash
        user = User(
            id=user_in_db.id,
            email=user_in_db.email,
            mobile=user_in_db.mobile,
            name=user_in_db.name,
            created_at=user_in_db.created_at,
            last_login=user_in_db.last_login,
            is_active=user_in_db.is_active,
        )

        return user, token

    def login(self, user_login: UserLogin) -> tuple[User, str]:
        """
        Login a user.
        
        Returns:
            Tuple of (User, access_token)
        
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user
        user_id = None
        user_in_db = None

        if user_login.email:
            result = self._find_user_by_email(user_login.email)
            if result:
                user_id, user_in_db = result
        elif user_login.mobile:
            result = self._find_user_by_mobile(user_login.mobile)
            if result:
                user_id, user_in_db = result

        if not user_in_db:
            raise ValueError("Invalid credentials")

        # Verify password
        if not self._verify_password(user_login.password, user_in_db.password_hash):
            raise ValueError("Invalid credentials")

        # Check if user is active
        if not user_in_db.is_active:
            raise ValueError("Account is inactive")

        # Update last login
        now = datetime.utcnow()
        users = self._load_users()
        user_in_db.last_login = now
        users[user_id] = user_in_db
        self._save_users(users)

        # Generate and save token
        token = self._generate_token()
        tokens = self._load_tokens()
        tokens[token] = {
            "user_id": user_id,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=7)).isoformat()
        }
        self._save_tokens(tokens)

        # Return user without password hash
        user = User(
            id=user_in_db.id,
            email=user_in_db.email,
            mobile=user_in_db.mobile,
            name=user_in_db.name,
            created_at=user_in_db.created_at,
            last_login=user_in_db.last_login,
            is_active=user_in_db.is_active,
        )

        return user, token

    def verify_token(self, token: str) -> Optional[User]:
        """
        Verify a token and return the associated user.
        """
        tokens = self._load_tokens()
        token_data = tokens.get(token)
        
        if not token_data:
            return None
            
        # Check expiry
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.utcnow() > expires_at:
            # Clean up expired token
            del tokens[token]
            self._save_tokens(tokens)
            return None
            
        user_id = token_data["user_id"]
        users = self._load_users()
        user_in_db = users.get(user_id)
        
        if not user_in_db or not user_in_db.is_active:
            return None
            
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            mobile=user_in_db.mobile,
            name=user_in_db.name,
            created_at=user_in_db.created_at,
            last_login=user_in_db.last_login,
            is_active=user_in_db.is_active,
        )


# Global auth service instance
auth_service = AuthService()
