"""Base model for API responses."""

from typing import Any, Dict

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


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
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary."""
        return cls(**data)
