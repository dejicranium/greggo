from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import transaction
from sqlalchemy.exc import DBAPIError

from ..form import (PollCreateForm,
    LoginForm)

from ..models.main_models import (User,
    Comment,
    Poll,
    Option,
    Category,
    TargetedPolls,
    PollCategory, Activity)

from ..services.follow_service import FollowService

from ..form import RegistrationForm
from pyramid.security import remember, forget

from ..services.follow_service import *


def get_followers_posts(request, user_id):
    polls = []
    user = request.dbsession.query(User).filter(User.id==user_id).first()
    followed = FollowService.get_following(request, user)

    if not followed:
        return None

    for followee in followed:
        for poll in followee.polls:
            polls.append(poll)

    return polls





def get_subscriptions(request, user):
    subscriptions = []
    for s in user.subscriptions:
        subscriptions.append(s.subscriptions)
    return subscriptions


def user_has_no_subscriptions(request, user):
    subscriptions = get_subscriptions(request, user)
    return len(subscriptions) == 0


def get_subscribed_posts(request, user):
    categories = request.dbsession.query(Category)
    relevant_categories= []
    relevant_polls = []
    relevant_categories = get_subscriptions(request, user)

    for category in relevant_categories:
        for p in category.polls:
            relevant_polls.append(p.polls)
    return relevant_polls


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def homepage_view(request):
    polls = request.dbsession.query(Poll)
    auth_user = request.user
    user = None
    if auth_user:
        user = request.dbsession.query(User).filter(User.id==auth_user.id).first()
        if not user_has_no_subscriptions(request, user):    #if user is subscribed to certain categories
            polls = get_subscribed_posts(request, user)
    options = request.dbsession.query(Option)
    categories = request.dbsession.query(Category)
    mypolls = None
    following = None

    if request.user:
        activities = FollowService.get_followees_activities(request, request.user)

        #polls
        ps = [activity for activity in activities if activity.activity_type == "poll"]
        mypolls = ps

    return { 'mypolls': mypolls,
            'page_title': 'home',
            'polls': polls,
            'followings':following,
            'categories': categories,
            'options': options,
            'users': user,
            'auth_user':auth_user}


"""
@view_config(route_name='home',
    renderer='../templates/mytemplate_mobile.jinja2', user_agent='mobile')
def homepage_mobile_view(request):
    auth_user = request.user
    user = None
    if not auth_user:
        polls = request.dbsession.query(Poll)
        return {'polls': polls}
    else:
        #get all polls
        polls = request.dbsession.query(Poll)
        user = request.dbsession.query(User).filter(User.id==auth_user.id).first()

        t_polls = []
        #iterate through every poll,
        #check if each is targeted.
        #if targeted, check whether the location is the same as the users
        #if it is, show it to the user
        #else, do not

        #for each in polls:
         #   if each.targeted == 1:
          #      poll = request.dbsession.query(TargetedPolls).filter(TargetedPolls.poll_id==each.id).first()
           #     if poll.location == auth_user.location:
            #        t_polls.append(each)
            #else:
             #   t_polls.append(each)

        t_polls = get_followers_activity(request, request.user)


        return {'polls': t_polls, 'user_id': request.user.id}

"""

@view_config(route_name='add_cat', renderer='../templates/show_categories.jinja2')
def add_categories(request):
   
    categories_from_file = []
    file = '/home/deji/Documents/repoll/repoll/views/categories.txt'
    with open(file) as fp:
        line = fp.readline()
        while line:
            new_cat = Category()
            new_cat.category_name = line
            request.dbsession.add(new_cat)
            line = fp.readline()
    categories = request.dbsession.query(Category)
    return {'categories': categories}

@view_config(route_name='add_categories', renderer='json')
def show_category(request):
    
    categories = request.dbsession.query(Category)
    categories_dict = {'categories': []}

    for category in categories:
        dictt = {}
        dictt['categoryName'] = category.category_name
        dictt['categoryId'] = category.id
        categories_dict['categories'].append(dictt)

    

    return categories_dict
    
    
@view_config(route_name='get_num_of_votes', renderer='json')
def get_votes(request):
    poll_id = request.matchdict.get('poll_id', -1)

    poll = request.dbsession.query(Poll).filter(Poll.id==poll_id).one()

    return {'votes':poll.num_of_votes}

@view_config(route_name='category', renderer='json')
def category(request):
    category_id = request.matchdict.get('category_id', -1)
    categories = request.dbsession.query(Category).filter(Category.id==category_id).all()
    posts_in_category =[]
    posts_title = []


    for category in categories:
        for a in category.polls:
            pollr = request.dbsession.query(Poll).filter_by(id=a.poll_id).all()
            for poll in pollr:
                posts_title.append(poll.question)


    return {'posts': "".join(posts_title)}



@view_config(route_name='test_mobile', renderer='json')
def test(request):
    return {'user_agnet' : "The user agent is not mobile"}

@view_config(route_name='test_mobile', renderer='json', user_agent='mobile')
def test_mobile(request):
    return {'user_agent': "The user agent is mobile"}


@view_config(route_name='activities', renderer='json')
def activities(request):
    activities = request.dbsession.query(Activity)
    sources = []
    dictt = {}

    for activity in activities:
        sources.append(get_source(request, activity))

    return {'sources': sources}
