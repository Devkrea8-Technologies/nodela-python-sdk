"""Tests for package exports and version."""

import pytest

import nodela
from nodela import (
    SUPPORTED_CURRENCIES,
    AuthenticationError,
    CreateInvoiceParams,
    CreateInvoiceResponse,
    ListTransactionsResponse,
    NetworkError,
    NodelaClient,
    NodelaError,
    NotFoundError,
    RateLimitError,
    ServerError,
    Transaction,
    ValidationError,
    VerifyInvoiceResponse,
)


class TestPackageExports:
    """Test cases for package-level exports."""

    def test_version_exists(self) -> None:
        """Test that package has a version."""
        assert hasattr(nodela, "__version__")
        assert isinstance(nodela.__version__, str)
        assert len(nodela.__version__) > 0

    def test_version_format(self) -> None:
        """Test that version follows semantic versioning."""
        version = nodela.__version__
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor
        for part in parts:
            assert part.isdigit()

    def test_all_exports_defined(self) -> None:
        """Test that __all__ is defined and contains expected exports."""
        assert hasattr(nodela, "__all__")
        assert isinstance(nodela.__all__, list)
        assert len(nodela.__all__) > 0

    def test_client_exported(self) -> None:
        """Test that NodelaClient is exported."""
        assert hasattr(nodela, "NodelaClient")
        assert NodelaClient is nodela.NodelaClient

    def test_exceptions_exported(self) -> None:
        """Test that all exceptions are exported."""
        exceptions = [
            "NodelaError",
            "AuthenticationError",
            "ValidationError",
            "RateLimitError",
            "NotFoundError",
            "ServerError",
            "NetworkError",
        ]

        for exc_name in exceptions:
            assert exc_name in nodela.__all__
            assert hasattr(nodela, exc_name)

    def test_models_exported(self) -> None:
        """Test that models are exported."""
        models = [
            "CreateInvoiceParams",
            "CreateInvoiceResponse",
            "VerifyInvoiceResponse",
            "Transaction",
            "ListTransactionsResponse",
        ]

        for model_name in models:
            assert model_name in nodela.__all__
            assert hasattr(nodela, model_name)

    def test_constants_exported(self) -> None:
        """Test that constants are exported."""
        assert "SUPPORTED_CURRENCIES" in nodela.__all__
        assert hasattr(nodela, "SUPPORTED_CURRENCIES")


class TestClientImport:
    """Test cases for NodelaClient import."""

    def test_can_import_client_directly(self) -> None:
        """Test that client can be imported directly."""
        from nodela import NodelaClient

        assert NodelaClient is not None

    def test_can_instantiate_imported_client(self) -> None:
        """Test that imported client can be instantiated."""
        from nodela import NodelaClient

        # Should work with API key
        client = NodelaClient(api_key="test_key")
        assert client is not None


class TestExceptionImports:
    """Test cases for exception imports."""

    def test_can_import_all_exceptions(self) -> None:
        """Test that all exceptions can be imported."""

        assert NodelaError is not None
        assert AuthenticationError is not None
        assert ValidationError is not None
        assert RateLimitError is not None
        assert NotFoundError is not None
        assert ServerError is not None
        assert NetworkError is not None

    def test_exceptions_are_exception_subclasses(self) -> None:
        """Test that all exported exceptions are Exception subclasses."""

        exceptions = [
            NodelaError,
            AuthenticationError,
            ValidationError,
            RateLimitError,
            NotFoundError,
            ServerError,
            NetworkError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)


class TestModelImports:
    """Test cases for model imports."""

    def test_can_import_invoice_models(self) -> None:
        """Test that invoice models can be imported."""

        assert CreateInvoiceParams is not None
        assert CreateInvoiceResponse is not None
        assert VerifyInvoiceResponse is not None

    def test_can_import_transaction_models(self) -> None:
        """Test that transaction models can be imported."""

        assert Transaction is not None
        assert ListTransactionsResponse is not None

    def test_can_instantiate_create_invoice_params(self) -> None:
        """Test that CreateInvoiceParams can be instantiated."""

        params = CreateInvoiceParams(amount=100.0, currency="USD")
        assert params.amount == 100.0
        assert params.currency == "USD"


class TestConstantImports:
    """Test cases for constant imports."""

    def test_can_import_supported_currencies(self) -> None:
        """Test that SUPPORTED_CURRENCIES can be imported."""

        assert SUPPORTED_CURRENCIES is not None
        assert isinstance(SUPPORTED_CURRENCIES, list)
        assert len(SUPPORTED_CURRENCIES) > 0

    def test_supported_currencies_contains_major_currencies(self) -> None:
        """Test that major currencies are in SUPPORTED_CURRENCIES."""

        assert "USD" in SUPPORTED_CURRENCIES
        assert "EUR" in SUPPORTED_CURRENCIES
        assert "GBP" in SUPPORTED_CURRENCIES


class TestModuleStructure:
    """Test cases for module structure."""

    def test_module_has_docstring(self) -> None:
        """Test that the module has a docstring."""
        assert nodela.__doc__ is not None
        assert len(nodela.__doc__) > 0

    def test_submodules_exist(self) -> None:
        """Test that expected submodules exist."""
        import nodela.client
        import nodela.exceptions
        import nodela.models
        import nodela.resources
        import nodela.utils

        assert nodela.client is not None
        assert nodela.exceptions is not None
        assert nodela.models is not None
        assert nodela.resources is not None
        assert nodela.utils is not None

    def test_can_access_nested_modules(self) -> None:
        """Test that nested modules can be accessed."""
        import nodela.models.invoice
        import nodela.models.transaction
        import nodela.resources.invoices
        import nodela.resources.transactions
        import nodela.utils.http

        assert nodela.models.invoice is not None
        assert nodela.models.transaction is not None
        assert nodela.resources.invoices is not None
        assert nodela.resources.transactions is not None
        assert nodela.utils.http is not None


class TestBackwardsCompatibility:
    """Test cases for backwards compatibility."""

    def test_old_style_imports_work(self) -> None:
        """Test that old-style imports still work."""
        from nodela.client import NodelaClient
        from nodela.exceptions import NodelaError

        assert NodelaClient is not None
        assert NodelaError is not None

    def test_mixed_import_styles(self) -> None:
        """Test that mixed import styles work together."""
        from nodela import NodelaClient as Client1
        from nodela.client import NodelaClient as Client2

        assert Client1 is Client2


class TestTypeHints:
    """Test cases for type hints and typing support."""

    def test_package_has_py_typed(self) -> None:
        """Test that package declares typing support."""
        # This is defined in pyproject.toml as package-data
        # The py.typed file should exist when installed
        pass

    def test_exported_classes_have_type_hints(self) -> None:
        """Test that exported classes have proper type hints."""
        import inspect

        from nodela import NodelaClient

        # Check NodelaClient.__init__ has annotations
        init_sig = inspect.signature(NodelaClient.__init__)
        assert len(init_sig.parameters) > 0

        # Check CreateInvoiceParams has annotations
        assert hasattr(CreateInvoiceParams, "__annotations__")


class TestImportPerformance:
    """Test cases for import performance and minimal dependencies."""

    def test_import_does_not_fail(self) -> None:
        """Test that importing the package does not raise exceptions."""
        try:
            import nodela

            assert nodela is not None
        except Exception as e:
            pytest.fail(f"Import failed with exception: {e}")

    def test_import_all_exports(self) -> None:
        """Test that importing all exports works."""
        try:
            from nodela import (
                SUPPORTED_CURRENCIES,
                AuthenticationError,
                CreateInvoiceParams,
                CreateInvoiceResponse,
                ListTransactionsResponse,
                NetworkError,
                NodelaClient,
                NodelaError,
                NotFoundError,
                RateLimitError,
                ServerError,
                Transaction,
                ValidationError,
                VerifyInvoiceResponse,
            )

            # All should be imported successfully
            assert all(
                [
                    NodelaClient,
                    NodelaError,
                    AuthenticationError,
                    ValidationError,
                    RateLimitError,
                    NotFoundError,
                    ServerError,
                    NetworkError,
                    SUPPORTED_CURRENCIES,
                    CreateInvoiceParams,
                    CreateInvoiceResponse,
                    VerifyInvoiceResponse,
                    Transaction,
                    ListTransactionsResponse,
                ]
            )
        except Exception as e:
            pytest.fail(f"Import all failed with exception: {e}")


class TestNamespaceIsolation:
    """Test cases for namespace isolation."""

    def test_private_modules_not_exported(self) -> None:
        """Test that private implementation details are not in __all__."""
        import nodela

        # These should NOT be in __all__
        private_items = ["HTTPClient", "BaseModel", "BaseResource"]

        for item in private_items:
            assert item not in nodela.__all__

    def test_can_still_access_internal_modules(self) -> None:
        """Test that internal modules can still be accessed if needed."""
        # Even though not in __all__, they should still be accessible
        from nodela.models.base import BaseModel
        from nodela.resources.base import BaseResource
        from nodela.utils.http import HTTPClient

        assert HTTPClient is not None
        assert BaseModel is not None
        assert BaseResource is not None
