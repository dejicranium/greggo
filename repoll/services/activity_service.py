from repoll.models.main_models import PollVotes, OpinionVotes, Activity, Comment, Vote, Poll, Agrees, Reply, Share, \
    Opinion, Like
from greggo.feed.base import *
import random
from greggo.storage.redis.category_subscription import *
from ..models.main_models import User, Activity, Following
from greggo.feed_managers.base import FeedManager
import transaction
import datetime
from dateutil import relativedelta



def get_hours_difference(now, then):
    difference = relativedelta.relativedelta(now, then)
    return difference.hours

class ActivityService:

    def __init__(self, request, activity_type, user, source, _object=None):
        self.request = request
        self.user = user
        self.source = source
        self.object = _object
        self.activity_type = activity_type
        self.source_id = self.source.id

        if self.object:
            self.object_id = self.object.id
        else:
            self.object_id = None
        self.object_owner_id = None
        self.object_name = None


        self.a = Activity()

    def create_new_activity(self):
        self._create_poll_activity()
        self.request.dbsession.add(self.a)
        self.request.dbsession.flush()

        #fanout activity to user
        FeedManager(self.user.id).create_activity(self.a.id)
 
    def _create_poll_activity(self):
        self.a.activity_type = self.activity_type
        self.a.user_id = self.user.id
        self.a.source_id = self.source_id

        if self.object:
            self.a.object_id = self.object_id

            if isinstance(self.object, Poll):
                self.a.object_owner_id = self.object.poser
                self.a.object_name = 'poll'

            if isinstance(self.object, Following):
                self.a.object_owner_id = self.object.id
                self.a.object_name = 'follow' 

            elif isinstance(self.object, Comment):
                self.a.object_owner_id = self.object.commenter_id
                self.a.object_name = 'comment'


            elif isinstance(self.object, Agrees):
                self.a.object_owner_id = self.object.user_id
                self.a.object_name = 'agree'

            elif isinstance(self.object, Vote):
                self.a.object_owner_id = self.object.voter_id
                self.a.object_name = 'vote'

            elif isinstance(self.object, Opinion):
                self.a.object_owner_id = self.object.user_id
                self.a.object_name = 'opinion'

            elif isinstance(self.object, Like):
                self.a.object_owner_id = self.object.user_id
                self.a.object_name = 'like'

            elif isinstance(self.object, Share):
                self.a.object_owner_id = self.object.user_id
                self.a.object_name = 'share'
            elif isinstance(self.object, Reply):
                self.a.object_owner_id = self.object.from_user
                self.a.object_name = 'reply'

    def get_activity(self):
        # this should be called after create_new_activity
        self.a.source = self.source     # we need the source
        self.a.object = self.object     # we need the object
        return self.a


def get_source(request, activity_instance):
    """
    Get an activity instance
    
    """
    _type = activity_instance.activity_type
    _id = activity_instance.source_id
    source = None

    if _type == 'comment':
        source = Comment
    elif _type == 'follow':
        source = Following
    elif _type == 'poll':
        source = Poll
    elif _type == 'poll_vote':
        source = PollVotes
    elif _type == 'agree':
        source = Agrees
    elif _type == 'opinion_vote':
        source = OpinionVotes
    elif _type == 'opinion':
        source = Opinion
    elif _type == 'like':
        source = Like
    elif _type == 'share':
        source = Share
    elif _type == 'reply':
        source = Reply

    # activity = request.dbsession.query(source).filter(source.id==_id)
    return source


def get_activities_by_similar_users(request, users):
    activities = request.dbsession.query(Activity).filter(Activity.user_id.in_(users)).distinct(Activity.id).limit(len(users)).all()
    activities = [activity.id for activity in activities]
    return activities


def get_user_activities(request, user_id):
    activities = request.dbsession.query(Activity).filter(Activity.user_id == user_id).limit(100)
    return activities

def get_latest_activities(request, user_id, already_shown, start=0, end=20):
	feed_manager = FeedManager(user_id)
	activities = feed_manager.get_user_feed()

	if len(activities)  < 20:
		user = request.dbsession.query(User).filter(User.id==user_id).first()
		subscriptions = [subscription.category_id for subscription in user.subscriptions]
		subscription = subscriptions[0]
		subscribers = CategorySubscription(subscription)
		subscribers = subscribers.get_subscribers()
		new_activities = get_activities_by_similar_users(request, subscribers)
		activities.extend(new_activities)
	return activities

"""
def get_latest_activities(request, user_id, already_shown, start=0, end=20):
    max_per_batch = 2

    user_feed = UserFeed(user_id)
    activities = user_feed.get_activities()[0:start + end]
    # remove the activities the user has already seen
    for activity in already_shown:
        activities.remove(activity)

    if len(activities) < max_per_batch:
        user = request.dbsession.query(User).filter(User.id == user_id).first()
        subscriptions = [subscription.category_id for subscription in user.subscriptions]

        while (len(activities)) < max_per_batch:
            random_category = random.sample(subscriptions, 1)

            category = CategorySubscription(random_category)
            subscribers = category.get_subscribers()

            subscribers = [int(subscriber.decode('utf-8')) for subscriber in subscribers]

            try:
                random_similar_users = random.sample(subscribers, 1)
            except:
                continue

            activities_by_similar_users = get_activities_by_similar_users(request, random_similar_users)
            activities.extend(activities_by_similar_users)

    elif len(activities) > max_per_batch:
        activities = activities[0: max_per_batch]

    return activities
"""