"""Unit tests for base model."""

from typing import Any, Dict, Optional

import pytest
from pydantic import Field
from pydantic import ValidationError as PydanticValidationError

from nodela.models.base import BaseModel


class SampleModel(BaseModel):
    """Sample model for testing BaseModel functionality."""

    id: str
    name: str
    age: Optional[int] = None
    email: Optional[str] = None


class StrictModel(BaseModel):
    """Model with field validation for testing."""

    id: str = Field(..., min_length=1)
    count: int = Field(..., ge=0)
    price: Optional[float] = Field(None, gt=0)


class TestBaseModel:
    """Test cases for BaseModel class."""

    def test_basic_initialization(self) -> None:
        """Test basic model initialization with required fields."""
        model = SampleModel(id="123", name="Test")
        assert model.id == "123"
        assert model.name == "Test"
        assert model.age is None
        assert model.email is None

    def test_initialization_with_optional_fields(self) -> None:
        """Test initialization with optional fields provided."""
        model = SampleModel(id="123", name="Test", age=25, email="test@example.com")
        assert model.id == "123"
        assert model.name == "Test"
        assert model.age == 25
        assert model.email == "test@example.com"

    def test_missing_required_field_raises_error(self) -> None:
        """Test that missing required fields raise validation error."""
        with pytest.raises(PydanticValidationError) as exc_info:
            SampleModel(id="123")  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_to_dict_basic(self) -> None:
        """Test to_dict method with basic data."""
        model = SampleModel(id="123", name="Test")
        result = model.to_dict()

        assert isinstance(result, dict)
        assert result == {"id": "123", "name": "Test"}

    def test_to_dict_with_optional_fields(self) -> None:
        """Test to_dict with optional fields."""
        model = SampleModel(id="123", name="Test", age=25, email="test@example.com")
        result = model.to_dict()

        assert result == {"id": "123", "name": "Test", "age": 25, "email": "test@example.com"}

    def test_to_dict_excludes_none(self) -> None:
        """Test that to_dict excludes None values."""
        model = SampleModel(id="123", name="Test", age=None)
        result = model.to_dict()

        assert "age" not in result
        assert "email" not in result
        assert result == {"id": "123", "name": "Test"}

    def test_from_dict_basic(self) -> None:
        """Test from_dict class method with basic data."""
        data: Dict[str, Any] = {"id": "123", "name": "Test"}
        model = SampleModel.from_dict(data)

        assert isinstance(model, SampleModel)
        assert model.id == "123"
        assert model.name == "Test"

    def test_from_dict_with_optional_fields(self) -> None:
        """Test from_dict with optional fields."""
        data: Dict[str, Any] = {
            "id": "456",
            "name": "Another Test",
            "age": 30,
            "email": "another@example.com",
        }
        model = SampleModel.from_dict(data)

        assert model.id == "456"
        assert model.name == "Another Test"
        assert model.age == 30
        assert model.email == "another@example.com"

    def test_from_dict_invalid_data_raises_error(self) -> None:
        """Test from_dict with invalid data raises error."""
        data: Dict[str, str] = {"id": "123"}  # Missing required 'name'

        with pytest.raises(PydanticValidationError):
            SampleModel.from_dict(data)

    def test_to_dict_from_dict_roundtrip(self) -> None:
        """Test that to_dict and from_dict are reversible."""
        original = SampleModel(id="789", name="Roundtrip Test", age=40)
        dict_data = original.to_dict()
        restored = SampleModel.from_dict(dict_data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.age == original.age

    def test_extra_fields_allowed(self) -> None:
        """Test that extra fields are allowed per model config."""
        data: Dict[str, Any] = {"id": "123", "name": "Test", "extra_field": "extra_value"}
        model = SampleModel.from_dict(data)

        # Model should accept extra fields
        assert model.id == "123"
        assert model.name == "Test"

    def test_field_validation(self) -> None:
        """Test field validation with constraints."""
        # Valid data
        model = StrictModel(id="test_id", count=5, price=10.5)
        assert model.id == "test_id"
        assert model.count == 5
        assert model.price == 10.5

    def test_field_validation_min_length(self) -> None:
        """Test min_length validation."""
        with pytest.raises(PydanticValidationError) as exc_info:
            StrictModel(id="", count=5)

        errors = exc_info.value.errors()
        assert any("id" in str(error["loc"]) for error in errors)

    def test_field_validation_greater_equal(self) -> None:
        """Test greater-than-or-equal validation."""
        with pytest.raises(PydanticValidationError):
            StrictModel(id="test", count=-1)

    def test_field_validation_greater_than(self) -> None:
        """Test greater-than validation for price."""
        with pytest.raises(PydanticValidationError):
            StrictModel(id="test", count=5, price=0)

        with pytest.raises(PydanticValidationError):
            StrictModel(id="test", count=5, price=-10.5)

    def test_validate_assignment(self) -> None:
        """Test that assignment validation is enabled."""
        model = SampleModel(id="123", name="Test")

        # This should work
        model.name = "Updated Name"
        assert model.name == "Updated Name"

    def test_populate_by_name(self) -> None:
        """Test populate_by_name config option."""
        # This is more relevant for models with field aliases
        data: Dict[str, str] = {"id": "123", "name": "Test"}
        model = SampleModel(**data)
        assert model.id == "123"
        assert model.name == "Test"

    def test_model_equality(self) -> None:
        """Test model equality comparison."""
        model1 = SampleModel(id="123", name="Test", age=25)
        model2 = SampleModel(id="123", name="Test", age=25)
        model3 = SampleModel(id="123", name="Different", age=25)

        assert model1 == model2
        assert model1 != model3

    def test_model_copy(self) -> None:
        """Test model copy functionality."""
        original = SampleModel(id="123", name="Test", age=25)
        copied = original.model_copy()

        assert copied.id == original.id
        assert copied.name == original.name
        assert copied.age == original.age
        assert copied is not original

    def test_model_copy_with_update(self) -> None:
        """Test model copy with updates."""
        original = SampleModel(id="123", name="Test", age=25)
        updated = original.model_copy(update={"name": "Updated", "age": 30})

        assert updated.id == "123"
        assert updated.name == "Updated"
        assert updated.age == 30
        assert original.name == "Test"  # Original unchanged
        assert original.age == 25

    def test_model_dump(self) -> None:
        """Test model_dump method."""
        model = SampleModel(id="123", name="Test", age=25)
        dumped = model.model_dump()

        assert dumped == {"id": "123", "name": "Test", "age": 25, "email": None}

    def test_model_dump_exclude_none(self) -> None:
        """Test model_dump with exclude_none."""
        model = SampleModel(id="123", name="Test")
        dumped = model.model_dump(exclude_none=True)

        assert dumped == {"id": "123", "name": "Test"}
        assert "age" not in dumped
        assert "email" not in dumped

    def test_model_json_schema(self) -> None:
        """Test that model can generate JSON schema."""
        schema = SampleModel.model_json_schema()

        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "name" in schema["properties"]
        assert "age" in schema["properties"]
        assert "email" in schema["properties"]
        assert "required" in schema
        assert "id" in schema["required"]
        assert "name" in schema["required"]
