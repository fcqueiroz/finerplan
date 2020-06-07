"""FinerPlan global configurations."""
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class Default(object):
    """Default configuration."""
    TESTING = False
    SECRET_KEY = os.getenv("FINERPLAN_SECRET_KEY")
    SQLITE_DATABASE = os.getenv("FINERPLAN_DATABASE")

    WTF_CSRF_ENABLED = True

    NAME = os.getenv("LOGNAME", 'anon').capitalize()


class Development(Default):
    """Development configuration."""
    SECRET_KEY = "finerplan"
    SQLITE_DATABASE = os.path.join(PROJECT_ROOT, "dev.db")

    EXPLAIN_TEMPLATE_LOADING = True


class Testing(Development):
    """Testing configuration."""
    TESTING = True
    SQLITE_DATABASE = ''  # The database is created and destroyed per app instance

    EXPLAIN_TEMPLATE_LOADING = False

    WTF_CSRF_ENABLED = False


def obtain_config_object(environment='production'):
    """Given an environment string returns the corresponding config object."""
    if environment == "production":
        return Default
    elif environment == "development":
        return Development
    elif environment == "testing":
        return Testing

    print("Unknown environment {}.".format(environment))
