"""FinerPlan global configurations."""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Default(object):
    """Default configuration."""
    TESTING = False
    SECRET_KEY = os.getenv("FINERPLAN_SECRET_KEY")
    DATABASE = os.getenv("FINERPLAN_DATABASE")

    WTF_CSRF_ENABLED = True


class Development(Default):
    """Development configuration."""
    SECRET_KEY = "finerplan"
    DATABASE = os.path.join(basedir, "dev.finerplan.db")


class Testing(Development):
    """Testing configuration."""
    TESTING = True
    DATABASE = ":memory:"

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
