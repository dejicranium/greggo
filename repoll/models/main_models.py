from .meta import Base
from webhelpers2.text import urlify
import datetime

from sqlalchemy import (Table,
    Column,
    Integer,
    Unicode,
    UnicodeText,
    DateTime,
    Float,
    String,
    ForeignKey)
from sqlalchemy.schema import UniqueConstraint

from repoll.utils import age_util
from dateutil import relativedelta

from sqlalchemy.orm import relationship, backref
from webhelpers2.date import distance_of_time_in_words, time_ago_in_words
from passlib.apps import custom_app_context

MONTH_MAPPING = {'1': 'Jan',
                '2': 'Feb',
                '3': 'Mar',
                '4': 'Apr',
                '5': 'May',
                '6': 'Jun',
                '7': 'Jul',
                '8': 'Aug',
                '9': 'Sep',
                '10': 'Oct',
                '11': 'Nov',
                '12': 'Dec'}

def compute_time_difference(date1, date2, suffix='ago'):
    difference = relativedelta.relativedelta(date1, date2)

    minutes_d = difference.minutes
    hours_d = difference.hours
    days_d = difference.days
    years_d = difference.years

    if minutes_d == 0:
        return time_ago_in_words(date2, granularity='second', round=True) + ' ' + suffix
    elif hours_d == 1 or hours_d > 1:
        return time_ago_in_words(date2, granularity='hour', round=True) + ' ' + suffix
    
    elif minutes_d > 0 or minutes_d < 59:
        return time_ago_in_words(date2, granularity='minute') + ' ' + suffix
        
    elif days_d == 1 or days_d > 1 or days_d < 7:
        return time_ago_in_words(date2, granularity='day') + ' ' + suffix

    elif days_d > 7 or years_d == 0:
        return MONTH_MAPPING[str(date2.month)] + str(date2.day) 
    
    else:
        return MONTH_MAPPING[str(date2.month)] + str(date2.day) + ", " + str(date2.year)






class ContextImage(Base):
    __tablename__ = 'context_images'
    id = Column(Integer, primary_key=True)
    image_link = Column(Unicode(255))
    poll_id = Column(Integer, ForeignKey('polls.id'), nullable=True)
    opinion_id = Column(Integer, ForeignKey('opinions.id'), nullable=True)


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    comments = relationship("Comment")
    replies = relationship("Reply")


class UserNotification(Base):
    __tablename__ = 'user_notifications'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    notification_id = Column(Integer, ForeignKey('users.id'), primary_key=True)


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action_type = Column(Unicode(255), nullable=False)
    source_type = Column(Unicode(255), nullable=False)
    source_id = Column(Integer, nullable=False)
    object_type = Column(Unicode(255), nullable=False)
    object_id = Column(Integer, nullable=False)
    status = Column(String, default='unseen')
    time_added = Column(DateTime)

    def __eq__(notif1, notif2):
        return notif1.id == notif2.id

    def __hash__(self):
        return hash(self.id)

    
class Share(Base):
    __tablename__ = 'shares'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reply_id = Column(Integer, ForeignKey('replies.id'), nullable=True)
    comment_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    opinion_id = Column(Integer, ForeignKey('opinions.id'), nullable=True)
    poll_id = Column(Integer, ForeignKey('polls.id'), nullable=True)
    date_added = Column(DateTime, default=datetime.datetime.utcnow())


class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True,)
    reply_id = Column(Integer, ForeignKey('replies.id'), nullable=True,)
    comment_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    reply_id = Column(Integer, ForeignKey('replies.id') )
    poll_id = Column(Integer, ForeignKey('polls.id'), nullable=True)
    date_added = Column(DateTime, default=datetime.datetime.utcnow())


class Reply(Base):
    __tablename__ = 'replies'
    id = Column(Integer, primary_key=True)
    from_user = Column(Integer, ForeignKey('users.id'), nullable=False)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))

    reply = Column(Unicode(255), nullable=False)
    to_user = Column(Integer, ForeignKey('users.id'), nullable=False) 
    likes = relationship('Like', backref='reply')
    shares = relationship("Share", backref='reply')
    num_of_replies = Column(Integer, default=0)

    num_of_shares = Column(Integer, default=0)
    num_of_likes = Column(Integer, default=0)

    opinion_id = Column(Integer, ForeignKey('opinions.id'), nullable=True)
    replied_id = Column(Integer, ForeignKey('replies.id'), nullable=True)

    replies = relationship('Reply', backref=backref('parent', remote_side=[id]))
    comment_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    date_added = Column(DateTime, default=datetime.datetime.utcnow())
    

class Opinion(Base):
    __tablename__ = 'opinions'
    id = Column(Integer, primary_key=True)
    opinion = Column(Unicode(255), nullable=False)
    options = relationship("Option")
    comments = relationship("Comment", backref='opinion')
    shares = relationship("Share", backref='opinion')
    agrees = relationship("Agrees", backref='opinion')
    context_images = relationship("ContextImage", backref='opinion')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    num_of_votes = Column(Integer, default=0)
    num_of_replies = Column(Integer, default=0)
    num_of_comments = Column(Integer, default=0)
    num_of_likes = Column(Integer, default=0)
    num_of_shares = Column(Integer, default=0)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)


    @property
    def time_added(self):
        now = datetime.datetime.utcnow()

        return compute_time_difference(now, self.date_added)


class Agrees(Base):
    __tablename__ = 'agrees'
    id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.id'))
    opinion_id = Column(Integer, ForeignKey('opinions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    option_id = Column(Integer, ForeignKey('options.id'))


class SeenResults(Base):
    """This model class records the people who chose "see results" on a poll

    """
    __tablename__ = 'seen_results'
    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'))
    voter_id = Column(Integer, ForeignKey('users.id'))


class ThoughtLeader(Base):
    """
    These class is actually to serve as an incentive to make people comment
    on stuff in pozeet. 

    Thought Leadership will rely on an algorithm whose critical metrics will be things
    like number of people who have aggreed to a comment and stuff like that.
    """
    
    __tablename__ = 'thought_leaders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    


class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'))   #tells us the user that acted
    activity_type = Column(Unicode(255))                #tells us the type of action taken

    source_id = Column(Integer)                         #tells us the table to look forward to
                                                        # get the core of the action. Thus, if
                                                        # the activity
                                                        # type is "commented on", we get data from comments


    object_name = Column(Unicode(255))
    object_id = Column(Integer)                         #get the item that is being acted on
                                                        #for example, a user might be commenting on another user's
                                                        #comment to a poll. Here, the object is a comment and we can derive the poll from that

    object_owner_id = Column(Integer, ForeignKey('users.id'))   #the owner of the object that is being acted upon
    created = Column(DateTime, default=datetime.datetime.utcnow())                                                            #we are talking about the creator of the poll, contest or survey;
                                                                #the owner of the comment that was agreed to,
                                                                #the owner of the comment that was commented on
                                                                #the person whose group was joined, etc.

    def __eq__(activity1, activity2):
        return activity1.id == activity2.id

    def __hash__(self):
        return hash(self.id)

class CategorySubscriber(Base):
    __tablename__ = 'category_subscribers'
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)


class PollVotes(Base):
    __tablename__ = 'poll_votes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    __table_args__ = (UniqueConstraint('user_id', 'poll_id', name='user_poll_uc'),)

class OpinionVotes(Base):
    __tablename__ = 'opinion_votes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    opinion_id = Column(Integer, ForeignKey('opinions.id'))
    __table_args__ = (UniqueConstraint('user_id', 'opinion_id', name='user_opinion_uc'),)

class Following(Base):
    __tablename__ = "followings"
    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey('users.id'),)
    followed_id = Column(Integer, ForeignKey('users.id'), )
    __table_args__ = (UniqueConstraint('follower_id', 'followed_id', name='follower_followed_uc'),)


class Business(Base):
    __tablename__ = 'businesses'
    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=True)
    location = Column(Unicode(255), nullable = True)
    channels = relationship("Channel", backref='owned_by')
    polls = relationship("Poll", backref='business_creator')

    date_joined = Column(DateTime, default=datetime.datetime.utcnow())
    last_logged_in = Column(DateTime, default=datetime.datetime.utcnow())

    account_number = Column(DateTime)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(Unicode(255), nullable=False)
    last_name = Column(Unicode(255), nullable=False)
    email = Column(Unicode(255), nullable=False, unique = True)
    username = Column(Unicode(255), nullable=True, unique=True)
    password = Column(Unicode(255), nullable=False)
    phone_number = Column(Unicode(255), nullable=True, unique=True)
    sex = Column(Unicode(255), nullable=False)

    profile_picture = Column(Unicode(255), nullable=True)

    birth_date = Column(Integer, nullable=True)
    birth_month = Column(Unicode(255), nullable=True)
    birth_year = Column(Integer, nullable=True)
    bio = Column(Unicode(255), nullable=True)

    country = Column(Integer, ForeignKey('countries.id'), nullable=True)
    sub_unit = Column(Integer, ForeignKey('sub_national.id'), nullable=True)
 
    polls = relationship("Poll", backref='added_by')
    polls_created = Column(Integer, default=0)
    polls_voted_in = relationship('PollVotes', backref='polls_voted_in', primaryjoin=id==PollVotes.user_id)
    opinions_voted_in = relationship('OpinionVotes', backref='opinions_voted_in', primaryjoin=id==OpinionVotes.user_id)
    polls_seen_results = relationship('SeenResults', backref='polls_seen_results',primaryjoin=id==SeenResults.voter_id)
    #let's deal with numbers her
    num_polls_voted_in = Column(Integer, default=0)
    num_of_followers = Column(Integer, default=0)
    num_of_followed = Column(Integer, default=0)

    comments = relationship("Comment", backref='added_by')

    opinions = relationship("Opinion", backref='added_by')
    likes = relationship("Like", backref='added_by')
    shares = relationship("Share", backref='added_by')
    votes = relationship("PollVotes",  backref='added_by')
    replies = relationship('Reply', backref='added_by', primaryjoin=id==Reply.from_user)
    replies_to = relationship('Reply', backref='user_replied_to', primaryjoin=id==Reply.to_user)

    date_joined = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    last_logged = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    
    notification_triggered = relationship('Notification', backref='triggered_by', primaryjoin=id==Notification.sender_id)
    followers = relationship('Following', backref='followers', primaryjoin=id==Following.followed_id)
    following = relationship('Following', backref='following', primaryjoin=id==Following.follower_id)

    subscriptions = relationship('CategorySubscriber',
        backref='subscribers',
        primaryjoin=id==CategorySubscriber.user_id)

    slug = Column(Unicode(255), nullable=True)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self


    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id==user.id).count()>0
    
    @property
    def age(self):
        return age_util.calculate_age(self.birth_date, self.birth_month, self.birth_year)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)


    def set_password(self, password):
        self.password = custom_app_context.encrypt(password)


    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def initials(self):
        return "{} {}.".format(self.first_name, self.last_name[0])

    #to be tested
    def get_studentship_status(self):
        now = datetime.datetime.utcnow()
        graduation = self.entrance_year

        if now > graduation:
            return "{} (Alumnus)".format(self.school)

        return "Student at {} ({})".format(self.school, self.graduation_year.year)


    def get_workplace(self):
        return "Works at {}".format(self.work_place)



    @property
    def job_information(self):
        return "Works at {}".format(work_place)





class PollCategory(Base):
    __tablename__ = 'poll_categories'
    poll_id = Column(Integer, ForeignKey('polls.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)


class TargetedPolls(Base):
    __tablename__ = 'targeted-polls'
    poll_id = Column(Integer, ForeignKey('polls.id'), primary_key=True)
    location = Column(Unicode(255), nullable=True)
    age = Column(Unicode(255), nullable=True)
    interest = Column(Unicode(255), nullable=True)
    work_place = Column(Unicode(255), nullable=True)

class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)

    question = Column(Unicode(255), nullable=True)

    poser = Column(Integer, ForeignKey('users.id'), nullable=True)  #user
    business_poser = Column(Integer, ForeignKey('businesses.id'), nullable=True) #business
    info_image_link = Column(Unicode(255), nullable=True)
    voters = Column(Integer, ForeignKey('users.id'), nullable=True)
    info = Column(Unicode(255))
    info_link_thumb =Column(Unicode(255), nullable=True)
    info_link_title =Column(Unicode(255), nullable=True)
    info_link_desc =Column(Unicode(255), nullable=True)

    date_edited = Column(DateTime, nullable=True)
    
    date_added = Column(DateTime, default=datetime.datetime.utcnow())
    num_of_votes = Column(Integer, default=0)
    num_of_comments = Column(Integer, default=0)
    num_of_shares = Column(Integer, default=0)
    num_of_likes = Column(Integer, default=0)

    slug = Column(Unicode(255))

    votes = relationship("Vote", backref='poll')
    options = relationship("Option")
    voters = relationship("PollVotes", backref='poll', primaryjoin=id==PollVotes.poll_id)
    comments = relationship("Comment", backref='poll')
    likes = relationship("Like", backref='poll')
    shares = relationship("Share", backref='poll')
    context_images = relationship("ContextImage", backref='poll')
    targeted = Column(Integer, default=0)   #to say whether the poll is targeted
                                            #or not. 0 is for not targeted
                                            #1 is for targeted.

    end_time = Column(DateTime, nullable=True)
    categories = relationship("PollCategory", backref='polls',
        primaryjoin=id == PollCategory.poll_id)

    in_channel = Column(Integer, ForeignKey('channels.id'))
    
    def has_ended(self):
        time_to_end = self.end_time
        now = datetime.datetime.utcnow()
        return now > time_to_end

    @property
    def slug(self):
        return urlify(self.question)

    @property
    def added_by(self):
        return self.poser.first_name

    @property
    def time_added(self):
        now = datetime.datetime.utcnow()

        return compute_time_difference(now, self.date_added)

    @property
    def time_edited(self):
        return distance_of_time_in_words(self.date_edited, granularity='hour') + " ago"

    @property
    def time_remaining(self):
        now = datetime.datetime.utcnow()
        return compute_time_difference(now, self.end_time, suffix='remaining')
    
    @property
    def number_of_votes(self):
        return self.votes

    @property
    def type(self):
        return "poll"

    @property
    def to_end(self):
        #return hours and minutes
        pass

    @property
    def has_ended(self):
        now = datetime.datetime.utcnow()
        to_end = self.end_time
        return now > self.end_time


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    business = Column(Integer, ForeignKey('businesses.id'))
    polls = relationship('Poll', backref='channel')


class Option(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    
    title = Column(Unicode(255), nullable = False) #every option has a title
    image_link = Column(Unicode(255), nullable=True) #needed when an option has an image attached to it

    opinion = Column(Integer, ForeignKey('opinions.id'), nullable=True)
    poll = Column(Integer, ForeignKey('polls.id'), nullable=True)
    num_of_votes = Column(Integer, default = 0)
    
    comments = relationship("Comment", backref='option')
    votes = relationship("Vote", backref='option')


class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'))
    option_id = Column(Integer, ForeignKey('options.id'))
    voter_id = Column(Integer, ForeignKey('users.id'))
    
    #put an index on this. Index poll_id

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    category_name = Column(Unicode(255), nullable=False)
    subscribers = relationship('CategorySubscriber',
        backref='subscriptions',
        primaryjoin=id==CategorySubscriber.category_id)

    polls = relationship("PollCategory",
        backref='categories',
        primaryjoin=id == PollCategory.category_id)


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    commenter_id = Column(Integer, ForeignKey('users.id'))
    comment = Column(Unicode(255))
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    option_id = Column(Integer, ForeignKey('options.id'))
    poll_id = Column(Integer, ForeignKey('polls.id'))
    opinion_id = Column(Integer, ForeignKey('opinions.id'))
    date_added = Column(DateTime, default=datetime.datetime.utcnow())
    replies = relationship('Reply', backref='comment', primaryjoin=id==Reply.comment_id)
    
    likes = relationship('Like', backref='comment')
    shares = relationship("Share", backref='comment')

    num_of_shares = Column(Integer, default=0)
    num_of_replies = Column(Integer, default=0)
    num_of_likes = Column(Integer, default=0)
    num_of_agrees = Column(Integer, default=0)
    

    @property
    def time_added(self):
        now = datetime.datetime.utcnow()
        return compute_time_difference(now, self.date_added)
    
    @property
    def type(self):
        return "comment"


class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    code = Column(Unicode(255), nullable=True)
    cities = relationship("City", backref='country')
    sub_nationals = relationship("SubNational", backref='country')

class SubNational(Base):
    __tablename__ = 'sub_national'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    code = Column(Unicode(255), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    cities = relationship("City", backref='subnational')


class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    code = Column(Unicode(255), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'))
    sub_national_id = Column(Integer, ForeignKey('sub_national.id'))
