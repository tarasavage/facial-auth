from unittest.mock import MagicMock, patch
import pytest
from s3.client import S3Client
from s3.exceptions import S3ClientError
from botocore.exceptions import ClientError


class TestS3Client:
    @pytest.fixture
    def s3_client_mock(self):
        return MagicMock()

    def test_s3_client_init_invalid_credentials(self):
        with pytest.raises(S3ClientError) as e:
            S3Client(aws_access_key_id="", aws_secret_access_key="", region_name="")
        assert str(e.value) == "Can't initialize S3 client"

    @patch("s3.client.client")
    def test_s3_client_init_client_error(self, mock_boto_client):
        mock_boto_client.side_effect = ClientError(error_response={"Error": {"Code": "403"}}, operation_name="test")
        with pytest.raises(S3ClientError) as e:
            S3Client(
                aws_access_key_id="test",
                aws_secret_access_key="test",
                region_name="test",
            )
        assert str(e.value) == "Failed to initialize S3 client"

    @patch("s3.client.client")
    def test_s3_client_init_success(self, mock_boto_client):
        mock_boto_client.return_value = MagicMock()
        access_key = "test"
        secret_key = "test"
        region = "test"
        s3_client = S3Client(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        assert s3_client is not None
        assert s3_client.client is not None

        mock_boto_client.assert_called_with(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
