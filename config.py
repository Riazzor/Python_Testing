import os


class DevelopmentConfig:
    DEBUG = True
    SECRET_KEY = 'something special'
    PATH = {
        'competitions': 'competitions.json',
        'clubs': 'clubs.json',
    }


class TestConfig(DevelopmentConfig):
    PATH = {
        'competitions': 'tests/fixtures/competitions_test.json',
        'clubs': 'tests/fixtures/clubs_test.json',
    }
    TESTING = True


class ProdConfig:
    pass


ENV = os.getenv('FLASK_ENV', 'DEVELOPMENT')


ENV_CONFIG = {
    'DEVELOPMENT': DevelopmentConfig,
    'TEST': TestConfig,
    'PROD': DevelopmentConfig,
}
config = ENV_CONFIG.get(ENV.upper())()
