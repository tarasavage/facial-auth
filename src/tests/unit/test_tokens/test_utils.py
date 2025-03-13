import tokens.utils as token_utils
import pytest
import jwt


class TestTokenUtils:
    @pytest.fixture
    def test_payload(self):
        return {"sub": "test"}

    def _assert_token_structure(self, token, expected_token_type):
        """Helper method to verify token structure and contents"""
        assert token is not None
        assert len(token.split(".")) == 3

        decoded = token_utils.decode_jwt(token)
        assert decoded is not None
        assert decoded["sub"] == "test"
        assert decoded["token_type"] == expected_token_type
        assert decoded["exp"] is not None
        assert decoded["iat"] is not None
        return decoded

    def test_create_access_token(self, test_payload):
        token = token_utils.create_access_token(test_payload)
        self._assert_token_structure(token, "access")

    def test_create_refresh_token(self, test_payload):
        token = token_utils.create_refresh_token(test_payload)
        self._assert_token_structure(token, "refresh")

    def test_access_token_decode(self, test_payload):
        token = token_utils.create_access_token(test_payload)
        decoded = token_utils.decode_jwt(token)

        assert decoded is not None
        assert decoded["sub"] == "test"
        assert decoded["token_type"] == "access"
        header, payload, signature = token.split(".")
        invalid_token = token_utils.create_access_token({"sub": "test2"})
        _, invalid_payload, invalid_signature = invalid_token.split(".")
        invalid_token = f"{header}.{invalid_payload}.{signature}"
        invalid_token_2 = f"{header}.{payload}.{invalid_signature}"

        with pytest.raises(jwt.InvalidTokenError):
            token_utils.decode_jwt(invalid_token)

        with pytest.raises(jwt.InvalidTokenError):
            token_utils.decode_jwt(invalid_token_2)

    def test_decode_jwt_incorrect_arguments(self):
        for arg in [None, 1, True, False, 1.0]:
            with pytest.raises(ValueError) as e:
                token_utils.decode_jwt(token="e.d.f", key="e.d.f", algorithm=arg)

            assert str(e.value) == "Algorithm must be a string"

        with pytest.raises(ValueError) as e:
            token_utils.decode_jwt(
                token="e.d.f", key="e.d.f", algorithm=["HS256", "HS384"]
            )

        assert str(e.value) == "Algorithm must be a string"

        with pytest.raises(ValueError) as e:
            token_utils.decode_jwt(token="e.d.f", key="e.d.f", algorithm="None")

        assert str(e.value) == "Secure algorithm is required"

        with pytest.raises(ValueError) as e:
            token_utils.decode_jwt(token=123, key="e.d.f", algorithm="HS256")

        assert str(e.value) == "Token must be a string or bytes"
