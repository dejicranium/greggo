import unittest
import transaction
from .security import *


from pyramid import testing
from passlib.apps import custom_app_context



def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        self.config.add_request_method(get_user, 'user', reify=True)

        settings = self.config.get_settings()

        from .models import (
            get_engine,
            get_session_factory,
            get_tm_session,
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from .models.meta import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

"""
class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        from .models import MyModel

        model = MyModel(name='one', value=55)
        self.session.add(model)

    def test_passing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'repoll')


class TestMyViewFailureCondition(BaseTest):

    def test_failing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info.status_int, 500)
"""

class TestFollowActions(BaseTest):

    def setUp(self):
        super(TestFollowActions, self).setUp()
        self.init_database()

        from .models import User 

        new_user = User(first_name="Someone", 
            last_name="Atoyebi",
            email='someone@gmail.com',
            password=custom_app_context.encrypt('int'))

        self.session.add(new_user)

    def test_user_details_not_unique(self):
        new_user = User(first_name="Someone", 
            last_name="Atoyebi",
            email='someone@gmail.com',
            password=custom_app_context.encrypt('int'))

        self.assertEqual(self.session.add(new_user), None)

    def test_user_details_unique(self):
        new_user = User(first_name="Someone", 
            last_name="Atoyebi",
            email='someone@gmaweil.com',
            password=custom_app_context.encrypt('int'))

        self.assertEqual(self.session.add(new_user), True)


