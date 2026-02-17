"""Base model for API responses."""

from __future__ import annotations

from typing import Any, Dict, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict

T = TypeVar("T", bound="BaseModel")


class BaseModel(PydanticBaseModel):
    """Base model for all API response models"""

    model_config = ConfigDict(
        extra="allow",
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dict(cls: type[T], data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        return cls(**data)
