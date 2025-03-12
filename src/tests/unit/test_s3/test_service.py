from io import BytesIO
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from s3.exceptions import S3ServiceError
from s3.service import S3Service


class TestS3Service:
    @pytest.fixture
    def s3_client_mock(self):
        return MagicMock()

    @pytest.fixture
    def s3_service(self, s3_client_mock):
        return S3Service(
            client=s3_client_mock,
            bucket_name="test-bucket",
        )

    def test_s3_service_init(self, s3_client_mock):
        s3_service = S3Service(
            client=s3_client_mock,
            bucket_name="test-bucket",
        )

        assert s3_service.client is not None
        assert s3_service.bucket_name == "test-bucket"

    def test_upload_object_ok(self, s3_service, s3_client_mock):
        test_file = b"test-file"
        test_key = "test-key"

        s3_service.upload_object(key=test_key, file=test_file)
        s3_client_mock.upload_fileobj.assert_called_once()

        args, kwargs = s3_client_mock.upload_fileobj.call_args
        assert isinstance(args[0], BytesIO)
        assert args[0].getvalue() == test_file
        assert args[1] == "test-bucket"
        assert args[2] == test_key
        assert kwargs == {}

    def test_upload_object_error(self, s3_service, s3_client_mock):
        s3_client_mock.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "400", "Message": "Bad Request"}},
            "Upload",
        )
        with pytest.raises(S3ServiceError) as e:
            s3_service.upload_object(key="test-key", file=b"test-file")

        assert str(e.value) == "Failed to upload object to S3"
