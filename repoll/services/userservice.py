from ..models.main_models import User, Poll, Option


class UserService(object):

    @classmethod
    def by_name(cls, request, email):
        return request.dbsession.query(User).filter(User.email == email).first()
