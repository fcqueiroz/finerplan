from app.models import User


def alice():
    user = User(
        username='Alice',
        email='alice@finerplan.com',
        password='nicepassword'
    )
    user.password = 'nicepassword'
    return user
