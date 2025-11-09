"""
Test suite for OAuth2 authentication implementation.

Tests verify ASVS 2.x and 3.x requirements for OAuth2:
- ASVS 2.1.5: Third-party authentication mechanisms
- ASVS 2.8.1: OAuth 2.0 authorization code flow
- ASVS 3.2.1: State parameter for CSRF protection
- ASVS 3.5.1: Secure token storage
"""

import pytest
import secrets
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestOAuth2AuthorizationURL:
    """Test OAuth2 authorization URL generation (ASVS 2.8.1)."""

    def test_generate_authorization_url_includes_required_parameters(self):
        """
        Test that authorization URL contains required OAuth2 parameters.

        ASVS 2.8.1: OAuth 2.0 clients use authorization code flow.

        Required parameters:
        - client_id
        - redirect_uri
        - response_type=code
        - scope
        - state (CSRF protection)
        """
        from secure_login import generate_oauth2_authorization_url

        client_id = "test-client-id"
        redirect_uri = "https://example.com/callback"
        scope = "openid profile email"

        url = generate_oauth2_authorization_url(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope
        )

        # Verify URL structure
        assert url.startswith("https://")
        assert "client_id=" + client_id in url
        assert "redirect_uri=" in url
        assert "response_type=code" in url
        assert "scope=" in url
        assert "state=" in url  # CSRF protection

    def test_authorization_url_state_is_cryptographically_random(self):
        """
        Test that state parameter is cryptographically secure (ASVS 3.2.1).

        State must be:
        - Cryptographically random (secrets module)
        - Unique per request
        - Sufficient length (at least 32 bytes)
        """
        from secure_login import generate_oauth2_authorization_url

        url1 = generate_oauth2_authorization_url(
            client_id="test",
            redirect_uri="https://example.com/callback",
            scope="openid"
        )

        url2 = generate_oauth2_authorization_url(
            client_id="test",
            redirect_uri="https://example.com/callback",
            scope="openid"
        )

        # Extract state parameters
        state1 = [p for p in url1.split('&') if p.startswith('state=')][0].split('=')[1]
        state2 = [p for p in url2.split('&') if p.startswith('state=')][0].split('=')[1]

        # Verify uniqueness
        assert state1 != state2

        # Verify length (URL-safe base64, at least 32 bytes = 43+ chars)
        assert len(state1) >= 43
        assert len(state2) >= 43


class TestOAuth2StateValidation:
    """Test OAuth2 state parameter validation (ASVS 3.2.1 - CSRF protection)."""

    def test_validate_state_accepts_valid_state(self):
        """Test that valid state parameter passes validation."""
        from secure_login import store_oauth2_state, validate_oauth2_state

        state = secrets.token_urlsafe(32)
        user_session_id = "test-session-123"

        # Store state
        store_oauth2_state(state, user_session_id)

        # Validate state
        is_valid = validate_oauth2_state(state, user_session_id)

        assert is_valid is True

    def test_validate_state_rejects_invalid_state(self):
        """Test that invalid state parameter fails validation."""
        from secure_login import validate_oauth2_state

        invalid_state = "invalid-state-value"
        user_session_id = "test-session-123"

        is_valid = validate_oauth2_state(invalid_state, user_session_id)

        assert is_valid is False

    def test_state_is_single_use_only(self):
        """
        Test that state parameter can only be used once.

        ASVS 3.2.1: Prevent replay attacks.
        """
        from secure_login import store_oauth2_state, validate_oauth2_state

        state = secrets.token_urlsafe(32)
        user_session_id = "test-session-123"

        store_oauth2_state(state, user_session_id)

        # First validation should succeed
        assert validate_oauth2_state(state, user_session_id) is True

        # Second validation should fail (state consumed)
        assert validate_oauth2_state(state, user_session_id) is False

    def test_state_expires_after_timeout(self):
        """
        Test that state parameter expires after reasonable time.

        ASVS 3.2.1: Time-limited state prevents delayed attacks.
        """
        from secure_login import store_oauth2_state, validate_oauth2_state

        state = secrets.token_urlsafe(32)
        user_session_id = "test-session-123"

        # Store state with timestamp in past (expired)
        with patch('secure_login.datetime') as mock_datetime:
            # Mock current time to 20 minutes ago
            past_time = datetime.utcnow() - timedelta(minutes=20)
            mock_datetime.utcnow.return_value = past_time

            store_oauth2_state(state, user_session_id)

        # Validate with current time - should fail (expired)
        is_valid = validate_oauth2_state(state, user_session_id)

        assert is_valid is False


class TestOAuth2TokenExchange:
    """Test OAuth2 authorization code exchange (ASVS 2.8.1)."""

    @patch('requests.post')
    def test_exchange_authorization_code_for_token(self, mock_post):
        """
        Test exchanging authorization code for access token.

        ASVS 2.8.1: OAuth 2.0 authorization code flow with token exchange.
        """
        from secure_login import exchange_oauth2_code_for_token

        # Mock successful token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'access-token-value',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'refresh-token-value',
            'id_token': 'id-token-value'
        }
        mock_post.return_value = mock_response

        code = "authorization-code-123"
        client_id = "test-client-id"
        client_secret = "test-client-secret"
        redirect_uri = "https://example.com/callback"

        tokens = exchange_oauth2_code_for_token(
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )

        # Verify token exchange request
        assert mock_post.called
        call_args = mock_post.call_args

        # Verify POST to token endpoint
        assert 'token' in call_args[0][0]  # URL contains 'token'

        # Verify request includes required parameters
        request_data = call_args[1]['data']
        assert request_data['grant_type'] == 'authorization_code'
        assert request_data['code'] == code
        assert request_data['client_id'] == client_id
        assert request_data['client_secret'] == client_secret
        assert request_data['redirect_uri'] == redirect_uri

        # Verify tokens returned
        assert tokens['access_token'] == 'access-token-value'
        assert tokens['refresh_token'] == 'refresh-token-value'

    @patch('requests.post')
    def test_token_exchange_validates_https(self, mock_post):
        """
        Test that token exchange enforces HTTPS.

        ASVS 2.8.3: OAuth endpoints must use TLS.
        """
        from secure_login import exchange_oauth2_code_for_token

        # This should raise an error for non-HTTPS
        with pytest.raises(ValueError, match="HTTPS required"):
            exchange_oauth2_code_for_token(
                code="code",
                client_id="id",
                client_secret="secret",
                redirect_uri="http://example.com/callback",  # HTTP not allowed
                token_endpoint="http://provider.com/token"  # HTTP not allowed
            )


class TestOAuth2UserInfo:
    """Test OAuth2 user information retrieval."""

    @patch('requests.get')
    def test_get_user_info_from_access_token(self, mock_get):
        """Test retrieving user information using access token."""
        from secure_login import get_oauth2_user_info

        # Mock user info response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'sub': '1234567890',
            'email': 'user@example.com',
            'email_verified': True,
            'name': 'Test User'
        }
        mock_get.return_value = mock_response

        access_token = "valid-access-token"
        user_info = get_oauth2_user_info(access_token)

        # Verify Authorization header
        call_args = mock_get.call_args
        assert call_args[1]['headers']['Authorization'] == f'Bearer {access_token}'

        # Verify user info returned
        assert user_info['sub'] == '1234567890'
        assert user_info['email'] == 'user@example.com'
        assert user_info['email_verified'] is True


class TestOAuth2Integration:
    """Integration tests for complete OAuth2 flow."""

    @patch('requests.get')
    @patch('requests.post')
    def test_complete_oauth2_login_flow(self, mock_post, mock_get):
        """
        Test complete OAuth2 authorization code flow.

        Steps:
        1. Generate authorization URL
        2. User redirected to provider (simulated)
        3. Provider callback with code and state
        4. Validate state
        5. Exchange code for tokens
        6. Retrieve user info
        7. Create/update local user
        8. Create session
        """
        from secure_login import (
            generate_oauth2_authorization_url,
            store_oauth2_state,
            validate_oauth2_state,
            exchange_oauth2_code_for_token,
            get_oauth2_user_info,
            create_or_update_oauth_user,
            create_session
        )

        # Step 1: Generate authorization URL
        auth_url = generate_oauth2_authorization_url(
            client_id="test-client",
            redirect_uri="https://app.com/callback",
            scope="openid profile email"
        )

        # Extract state from URL
        state = [p.split('=')[1] for p in auth_url.split('&') if p.startswith('state=')][0]

        # Step 2: Store state
        session_id = "session-123"
        store_oauth2_state(state, session_id)

        # Step 3: Simulate provider callback
        returned_code = "auth-code-from-provider"
        returned_state = state

        # Step 4: Validate state
        assert validate_oauth2_state(returned_state, session_id) is True

        # Step 5: Mock token exchange
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'access-123',
            'token_type': 'Bearer',
            'id_token': 'id-123'
        }

        tokens = exchange_oauth2_code_for_token(
            code=returned_code,
            client_id="test-client",
            client_secret="test-secret",
            redirect_uri="https://app.com/callback"
        )

        # Step 6: Mock user info retrieval
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'sub': 'oauth-user-123',
            'email': 'oauth@example.com',
            'email_verified': True,
            'name': 'OAuth User'
        }

        user_info = get_oauth2_user_info(tokens['access_token'])

        # Step 7: Create/update local user
        user_id = create_or_update_oauth_user(
            provider='google',
            provider_user_id=user_info['sub'],
            email=user_info['email'],
            name=user_info.get('name')
        )

        # Step 8: Create session
        session_id = create_session(user_id)

        assert session_id is not None
        assert len(session_id) >= 32  # Secure session ID
