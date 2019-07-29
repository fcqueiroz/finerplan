import pytest

from finerplan.model import User

from tests.data import users


@pytest.mark.usefixtures('db_session')
def test_create_user():
    user_data = users.alice()
    return_value = User.create(**user_data)

    new_user = User.query.filter_by(username=user_data['username'], email=user_data['email']).first()

    assert return_value == new_user
    assert new_user is not None
    assert new_user.check_password(password=user_data['password'])
    assert new_user.accounts.count() == 0
