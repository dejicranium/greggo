from ..models.main_models import (
    Following,
    User,
    Activity,
)
import transaction
from greggo.storage.redis.user_followings_storage import *
from repoll.services.activity_service import ActivityService
from repoll.services.notification_service import NotificationService

"""
Class made up of utility methods concerning follow relationships.

Note: this has been tested and is working appropriately. Yaay!

"""


class FollowService:
    @classmethod
    def follow_user(cls, request, user_id, followed_user_id):
        if followed_user_id == user_id:
            return None
		
        user_object = request.dbsession.query(User).filter(User.id == user_id)
        followed_user_object = request.dbsession.query(User).filter(User.id == followed_user_id)

        user = user_object.first()
        followed_user = followed_user_object.first()

        new_relationship = Following()
        new_relationship.follower_id = user_id
        new_relationship.followed_id = followed_user_id

        user.following.append(new_relationship)
        followed_user.followers.append(new_relationship)

        followed_user_object.update({'num_of_followers': (User.num_of_followers + 1) })
        user_object.update({"num_of_followed" : (User.num_of_followed + 1)})

        new_activity = ActivityService(request, 'follow', user, new_relationship, followed_user)
        new_activity.create_new_activity()
        activity = new_activity.get_activity()

        user_id = followed_user.id
        sender_id = new_relationship.follower_id
        activity_type = activity.activity_type
        source = new_relationship
        _object = followed_user

        notif = NotificationService(request, user_id, sender_id, activity_type, source, _object)
        notif.create_new_notification()
        transaction.commit()
    # user.following.append(new_relationship)
        request.dbsession.add(new_relationship)
        transaction.commit()


    @classmethod
    def unfollow_user(cls, request, user_id, user_to_unfollow_id):
        try:
            user_object =  request.dbsession.query(User).filter(User.id == user_id)
            user_to_unfollow_object = request.dbsession.query(User).filter(User.id == user_to_unfollow_id)

            the_relationship = request.dbsession.query(Following).filter(Following.follower_id==user_id, Following.followed_id==user_to_unfollow_id)

            #delete relationship
            the_relationship.delete()

            user_object.update({'num_of_followed': (User.num_of_followed - 1)})
            user_to_unfollow_object.update({"num_of_followers": (User.num_of_followers - 1)})
            transaction.commit()
        except:
            return Exception

        


    @classmethod
    def get_followers(cls, request, user):
        followers = []
        user_id = user.id
        for each in user.followers:
            ffls = request.dbsession.query(User).filter_by(id=each.follower_id).all()
            for follower in ffls:
                followers.append(follower.id)
        return followers


# all of these is totally wrong

    @classmethod
    def get_following(cls, request, user):
        followings = []
        for each in user.following:
            ffls = request.dbsession.query(User).filter_by(id=each.followed_id).all()
            for followee in ffls:
                followings.append(followee.first_name)
        return followings


@classmethod
def get_followers_ids(cls, request, user):
    followers_ids = []
    for each in user.followers:
        ffls = request.dbsession.query(User).filter_by(id=each.follower_id).all()
        for follower in ffls:
            followers_ids.append(follower.id)
    return followers_ids


@classmethod
def get_followees_ids(cls, request, user):
    followings_ids = []
    for each in user.following:
        ffls = request.dbsession.query(User).filter_by(id=each.followed_id).all()
        for followees in ffls:
            followings_ids.append(followees.id)


    return followings_ids


@classmethod
def get_followers_activities(cls, request, user):
    followers_ids = cls.get_followers_ids(request, user)
    flls_activities = request.dbsession.query(Activity).filter(Activity.user_id.in_(followers_ids)).all()
    return flls_activities


@classmethod
def get_followees_activities(cls, request, user):
    followees_ids = cls.get_followees_ids(request, user)
    if followees_ids:
        flls_activities = request.dbsession.query(Activity).filter(Activity.user_id.in_(followees_ids)).all()
        return flls_activities
    else:
        return []
