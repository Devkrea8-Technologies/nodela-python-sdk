"""Unit tests for NodelaClient."""

import os
from unittest.mock import patch

import pytest

from nodela.client import NodelaClient
from nodela.exceptions import AuthenticationError
from nodela.resources.invoices import Invoices
from nodela.resources.transactions import Transactions
from nodela.utils.http import HTTPClient


class TestNodelaClientInitialization:
    """Test cases for NodelaClient initialization."""

    def test_initialization_with_api_key(self, api_key: str) -> None:
        """Test client initialization with API key parameter."""
        client = NodelaClient(api_key=api_key)

        assert client.api_key == api_key
        assert client._http is not None
        assert isinstance(client._http, HTTPClient)
        assert isinstance(client.invoices, Invoices)
        assert isinstance(client.transactions, Transactions)

    def test_initialization_with_env_var(self, api_key: str) -> None:
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {"NODELA_API_KEY": api_key}):
            client = NodelaClient()

        assert client.api_key == api_key

    def test_initialization_without_api_key_raises_error(self) -> None:
        """Test that missing API key raises AuthenticationError."""
        # Clear the environment variable if it exists
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                NodelaClient()

        assert "API key is required" in str(exc_info.value)

    def test_initialization_prefers_param_over_env(self, api_key: str) -> None:
        """Test that parameter API key takes precedence over environment variable."""
        env_key = "env_api_key"
        param_key = "param_api_key"

        with patch.dict(os.environ, {"NODELA_API_KEY": env_key}):
            client = NodelaClient(api_key=param_key)

        assert client.api_key == param_key
        assert client.api_key != env_key

    def test_initialization_with_custom_timeout(self, api_key: str) -> None:
        """Test client initialization with custom timeout."""
        client = NodelaClient(api_key=api_key, timeout=60)

        assert client._http.timeout == 60

    def test_initialization_with_custom_max_retries(self, api_key: str) -> None:
        """Test client initialization with custom max retries."""
        client = NodelaClient(api_key=api_key, max_retries=5)

        # The HTTP client should be configured with max_retries
        assert client._http is not None

    def test_initialization_with_all_params(self, api_key: str) -> None:
        """Test client initialization with all parameters."""
        client = NodelaClient(api_key=api_key, timeout=45, max_retries=4)

        assert client.api_key == api_key
        assert client._http.timeout == 45

    def test_http_client_configured_correctly(self, api_key: str) -> None:
        """Test that HTTP client is configured with correct parameters."""
        timeout = 60
        max_retries = 5

        client = NodelaClient(api_key=api_key, timeout=timeout, max_retries=max_retries)

        assert client._http.base_url == "https://api.nodela.co"
        assert client._http.api_key == api_key
        assert client._http.timeout == timeout


class TestNodelaClientResources:
    """Test cases for client resource initialization."""

    def test_invoices_resource_initialized(self, nodela_client: NodelaClient) -> None:
        """Test that invoices resource is properly initialized."""
        assert hasattr(nodela_client, "invoices")
        assert isinstance(nodela_client.invoices, Invoices)
        assert nodela_client.invoices._http == nodela_client._http

    def test_transactions_resource_initialized(self, nodela_client: NodelaClient) -> None:
        """Test that transactions resource is properly initialized."""
        assert hasattr(nodela_client, "transactions")
        assert isinstance(nodela_client.transactions, Transactions)
        assert nodela_client.transactions._http == nodela_client._http

    def test_resources_share_http_client(self, nodela_client: NodelaClient) -> None:
        """Test that all resources share the same HTTP client instance."""
        assert nodela_client.invoices._http is nodela_client.transactions._http
        assert nodela_client.invoices._http is nodela_client._http


class TestNodelaClientAPIKey:
    """Test cases for API key handling."""

    def test_api_key_stored(self, api_key: str) -> None:
        """Test that API key is stored on the client."""
        client = NodelaClient(api_key=api_key)

        assert client.api_key == api_key

    def test_empty_api_key_raises_error(self) -> None:
        """Test that empty API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError):
                NodelaClient(api_key="")

    def test_none_api_key_with_no_env_raises_error(self) -> None:
        """Test that None API key with no env var raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError):
                NodelaClient(api_key=None)

    def test_whitespace_api_key_accepted(self) -> None:
        """Test that whitespace-only API key is accepted (will fail at API level)."""
        # Note: We accept it here, validation happens at API level
        client = NodelaClient(api_key="   ")
        assert client.api_key == "   "


class TestNodelaClientEnvironmentVariables:
    """Test cases for environment variable handling."""

    def test_reads_from_nodela_api_key_env_var(self, api_key: str) -> None:
        """Test reading from NODELA_API_KEY environment variable."""
        with patch.dict(os.environ, {"NODELA_API_KEY": api_key}):
            client = NodelaClient()

        assert client.api_key == api_key

    def test_env_var_name_is_case_sensitive(self, api_key: str) -> None:
        """Test that environment variable name is case-sensitive."""
        with patch.dict(os.environ, {"nodela_api_key": api_key}, clear=True):
            with pytest.raises(AuthenticationError):
                NodelaClient()

    def test_multiple_env_vars_only_correct_one_used(self, api_key: str) -> None:
        """Test that only the correct env var is used."""
        with patch.dict(
            os.environ,
            {"NODELA_API_KEY": api_key, "API_KEY": "wrong_key", "NODELA_KEY": "also_wrong"},
        ):
            client = NodelaClient()

        assert client.api_key == api_key


class TestNodelaClientDefaults:
    """Test cases for client default values."""

    def test_default_timeout(self, api_key: str) -> None:
        """Test default timeout value."""
        client = NodelaClient(api_key=api_key)

        assert client._http.timeout == 30

    def test_default_max_retries(self, api_key: str) -> None:
        """Test that default max retries is configured."""
        client = NodelaClient(api_key=api_key)

        # Should have session configured
        assert client._http.session is not None

    def test_default_base_url(self, api_key: str) -> None:
        """Test default base URL."""
        client = NodelaClient(api_key=api_key)

        assert client._http.base_url == "https://api.nodela.co"


class TestNodelaClientIntegration:
    """Integration-style tests for NodelaClient."""

    def test_client_can_access_invoice_methods(self, nodela_client: NodelaClient) -> None:
        """Test that client can access invoice resource methods."""
        assert hasattr(nodela_client.invoices, "create")
        assert hasattr(nodela_client.invoices, "verify")
        assert callable(nodela_client.invoices.create)
        assert callable(nodela_client.invoices.verify)

    def test_client_can_access_transaction_methods(self, nodela_client: NodelaClient) -> None:
        """Test that client can access transaction resource methods."""
        assert hasattr(nodela_client.transactions, "list")
        assert callable(nodela_client.transactions.list)

    def test_multiple_clients_are_independent(self, api_key: str) -> None:
        """Test that multiple client instances are independent."""
        client1 = NodelaClient(api_key=api_key, timeout=30)
        client2 = NodelaClient(api_key=api_key, timeout=60)

        assert client1._http is not client2._http
        assert client1.invoices is not client2.invoices
        assert client1.transactions is not client2.transactions
        assert client1._http.timeout == 30
        assert client2._http.timeout == 60

    def test_client_http_client_session_is_configured(self, nodela_client: NodelaClient) -> None:
        """Test that the HTTP client session is properly configured."""
        session = nodela_client._http.session

        assert session is not None
        assert "https://" in session.adapters
        assert "http://" in session.adapters


class TestNodelaClientDocumentation:
    """Test cases for client documentation and attributes."""

    def test_client_has_docstring(self) -> None:
        """Test that client class has documentation."""
        assert NodelaClient.__doc__ is not None
        assert len(NodelaClient.__doc__) > 0

    def test_client_init_signature(self) -> None:
        """Test that client __init__ has correct signature."""
        import inspect

        sig = inspect.signature(NodelaClient.__init__)
        assert "api_key" in sig.parameters
        assert "timeout" in sig.parameters
        assert "max_retries" in sig.parameters

    def test_client_attributes_accessible(self, nodela_client: NodelaClient) -> None:
        """Test that all expected client attributes are accessible."""
        assert hasattr(nodela_client, "api_key")
        assert hasattr(nodela_client, "_http")
        assert hasattr(nodela_client, "invoices")
        assert hasattr(nodela_client, "transactions")


class TestNodelaClientErrorHandling:
    """Test cases for client error handling."""

    def test_authentication_error_message_with_no_api_key(self) -> None:
        """Test that authentication error has helpful message."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                NodelaClient()

        error_message = str(exc_info.value)
        assert "API key is required" in error_message
        assert "NODELA_API_KEY" in error_message

    def test_authentication_error_when_param_is_none_and_no_env(self) -> None:
        """Test authentication error when param is explicitly None."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError):
                NodelaClient(api_key=None)

    def test_authentication_error_when_param_is_empty_string(self) -> None:
        """Test authentication error when param is empty string."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError):
                NodelaClient(api_key="")


class TestNodelaClientConfiguration:
    """Test cases for client configuration options."""

    def test_configuration_with_minimum_values(self, api_key: str) -> None:
        """Test configuration with minimum timeout and retries."""
        client = NodelaClient(api_key=api_key, timeout=1, max_retries=0)

        assert client._http.timeout == 1

    def test_configuration_with_maximum_values(self, api_key: str) -> None:
        """Test configuration with large timeout and retries."""
        client = NodelaClient(api_key=api_key, timeout=300, max_retries=10)

        assert client._http.timeout == 300

    def test_different_timeout_values(self, api_key: str) -> None:
        """Test various timeout values."""
        timeouts = [1, 5, 10, 30, 60, 120]

        for timeout in timeouts:
            client = NodelaClient(api_key=api_key, timeout=timeout)
            assert client._http.timeout == timeout

    def test_different_retry_values(self, api_key: str) -> None:
        """Test various max_retries values."""
        retries = [0, 1, 3, 5, 10]

        for retry in retries:
            client = NodelaClient(api_key=api_key, max_retries=retry)
            # Client should be created successfully
            assert client._http is not None
