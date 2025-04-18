from unittest.mock import MagicMock, AsyncMock

import pytest
from users.models import User
from users.repo import UsersUnitOfWork, UserRepository


class TestUserUnitOfWork:
    @pytest.fixture
    def session(self):
        return MagicMock()

    @pytest.fixture
    def async_session(self):
        return AsyncMock()

    def test_init(self, session):
        uow = UsersUnitOfWork(session=session)

        assert uow.session is not None
        assert uow.user_repo is not None
        assert uow.user_repo.session is session

    async def test_aenter_aexit(self, async_session):
        async with UsersUnitOfWork(session=async_session) as uow:
            assert uow.session is async_session
            assert isinstance(uow, UsersUnitOfWork)

        assert async_session.close.called

    def test_error_for_sync_session(self, session):
        with pytest.raises(TypeError):
            with UsersUnitOfWork(session=session):
                pass


class TestUserRepository:
    @pytest.fixture
    def async_session(self):
        return AsyncMock()

    @pytest.fixture
    def repo(self, async_session):
        return UserRepository(session=async_session)

    def test_init(self, async_session):
        repo = UserRepository(session=async_session)

        assert repo.session is async_session
        assert repo.model is User

    async def test_create_user_success(self, repo):
        user = {"username": "John Doe", "email": "john.doe@example.com"}
        user = await repo.create(user)

        repo.session.add.assert_called_with(user)
        repo.session.flush.assert_called_with()
        repo.session.refresh.assert_called_with(user)

        assert isinstance(user, User)
        assert user.username == "John Doe"
        assert user.email == "john.doe@example.com"
