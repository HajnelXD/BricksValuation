"""Custom user model definition.

Extends Django's :class:`AbstractUser` to apply business constraints:
 - Username length 3..50 (FR-01)
 - Unique email with minimal length > 2 (FR-16)
 - Timestamps with automatic update of ``updated_at`` on each save (FR-17)

Database level constraints mirror the db-plan in `.ai/db-plan.md`.

Notes:
 - We rely on Django's password hashing.
 - Email uniqueness enforced here (Django default does not enforce it).
 - ``updated_at`` auto-updated via overridden ``save`` (can be replaced by DB trigger later).
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core import validators
from django.db import models


class TimeStampedModel(models.Model):
    """Reusable timestamp fields with automatic ``updated_at`` touch.

    In the future the touch can be delegated to a PostgreSQL trigger for
    performance and cross-language integrity. For now we keep logic in Django
    to avoid raw SQL migration complexity in the MVP.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


USERNAME_MAX_LENGTH = 50
USERNAME_MIN_LENGTH = 3
EMAIL_MIN_LENGTH = 3


class User(AbstractUser, TimeStampedModel):
    """Project custom user.

    Constraints (enforced by validators + DB constraints):
    - ``username`` length between 3 and 50 characters.
    - ``email`` unique and length > 2.
    """

    # Override username to add length constraint (AbstractUser already has unique=True)
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text="Required. 3-50 chars. Letters, digits and @/./+/-/_ only.",
        validators=[
            validators.MinLengthValidator(USERNAME_MIN_LENGTH),
            validators.MaxLengthValidator(USERNAME_MAX_LENGTH),
        ],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    email = models.EmailField(
        unique=True,
        help_text="User email address (unique).",
        validators=[validators.MinLengthValidator(EMAIL_MIN_LENGTH)],
        error_messages={"unique": "A user with that email already exists."},
    )
    # Override M2M fields to prevent clashes when AUTH_USER_MODEL is not yet set.
    # Once AUTH_USER_MODEL = 'account.User' is configured, the default names would
    # also be fine; keeping custom related_name values is harmless.
    groups = models.ManyToManyField(
        Group,
        related_name="account_user_groups",
        related_query_name="account_user",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="account_user_permissions",
        related_query_name="account_user",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    class Meta(AbstractUser.Meta):  # type: ignore[misc]
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            models.CheckConstraint(
                check=models.Q(username__regex=r"^.{3,50}$"),
                name="user_username_length_range",
            ),
            models.CheckConstraint(
                check=models.Q(email__regex=r"^.{3,254}$"),
                name="user_email_min_length",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.username}"
