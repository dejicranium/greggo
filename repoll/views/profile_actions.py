from pyramid.view import view_config
from ..models.main_models import *

from greggo.storage.redis.voters_age_storage import PollVotersAgeStorage
from greggo.storage.redis.voters_gender_storage import PollVotersGenderStorage
from greggo.config import REDIS_SERVER

from ..utils.scraper_util import get_page_thumb_title_desc, url_exists, get_first_url
from ..utils.compile_util import compile_poll_details, compile_opinion_details
from pyramid.response import Response
import transaction
from pyramid.httpexceptions import HTTPFound
import uuid
from sqlalchemy import or_, and_
from ..services.activity_service import get_source


@view_config(route_name='view_profile', renderer='../templates/profile_page_mobile.jinja2')
def view_profile(request):
    from repoll.services.follow_service import FollowService

    user = None
    user_id = request.matchdict.get('user_id', -1)
    user_slug = request.matchdict.get('user_slug', None)
    user_is_self = False
    polls = []
    is_following = False

    if request.user: 
        user_is_self = request.user.id == int(user_id)
        user = request.dbsession.query(User).filter(User.id == user_id, User.slug==user_slug).first()
        user_followers = FollowService.get_followers(request, user)
        is_following = request.user.id in user_followers
        polls = reversed(user.polls[0:30])

    if is_following == True: 
        is_following = 'true'
    else: 
        is_following = 'false'
    return {'user': user, 'polls': polls, 'user_is_self': user_is_self, 'is_following': is_following}


@view_config(route_name='get_user_polls', renderer='json')
def get_user_polls(request):
    user_id = request.matchdict.get('user_id', None)
    dictt = []
    if user_id:
        user = request.dbsession.query(User).filter(User.id == user_id).first()
        for poll in user.polls:
            poll_dictt = compile_poll_details(request, poll, request.user)
            dictt.append(poll_dictt)
        return {'activities': {'polls': dictt}}


@view_config(route_name='get_comment_and_replies', renderer='json')
def get_comment_and_replies(request):
    user_id = request.matchdict.get('user_id', None)
    dictt = {'c_and_s': []}
    if user_id:
        activities = request.dbsession.query(Activity).filter(Activity.user_id == user_id, (Activity.activity_type == 'comment') | (Activity.activity_type == 'reply'))

        for activity in activities:
            source = get_source(request, activity)
            source_id = activity.source_id
            activity = request.dbsession.query(source).filter(source.id == source_id).first()
            object_is_poll = None
            object_is_opinion = None

            if source == Comment:
                try:
                    object_is_poll = activity.poll != None
                except Exception as e:
                    print(e)

                try:
                    object_is_opinion = activity.opinion != None

                except Exception as e:
                    print(e)

                comment_dictt = {
                    'type': 'comment',
                    'comment_id': activity.id,
                    'commenterInitals': activity.added_by.initials,
                    'commenter': activity.added_by.full_name,
                    'comment': activity.comment,
                    'option_chosen': activity.option.title,
                    'poll': activity.poll.question if object_is_poll else None,  # remember to add object
                    'opinion': activity.opinion.opinion if object_is_opinion else None
                }
                if object_is_poll:
                    comment_dictt['poll'] = {
					    'userName': activity.poll.added_by.full_name, 
					    'question': activity.poll.question,
					    'slug': activity.poll.slug, 
					
				    }
                if object_is_opinion:
                    comment_dictt['opinion'] = {
                        'userName': activity.opinion.added_by.full_name,
                        'opinion': activity.opinion.opinion,
                    }
                dictt['c_and_s'].append(comment_dictt)

    return dictt


@view_config(route_name='get_likes_and_shares', renderer='json')
def get_likes_and_shares(request):
    user_id = request.matchdict.get('user_id', None)
    dictt = {'l_and_s': []}
    if user_id:
        activities = request.dbsession.query(Activity).filter(Activity.user_id == user_id, (Activity.activity_type == 'like') | (Activity.activity_type == 'share'))

        for activity in activities:
            source = get_source(request, activity)
            source_id = activity.source_id
            activity = request.dbsession.query(source).filter(source.id == source_id).first()
            object_is_poll = None
            object_is_opinion = None
            object_is_comment =  None
            object_is_reply = None

            if source == Share:
                try:
                    object_is_poll = activity.poll != None
                except Exception as e:
                    print(e)

                try:
                    object_is_opinion = activity.opinion != None

                except Exception as e:
                    print(e)

                try:
                    object_is_comment = activity.comment != None
                except Exception as e:
                    print(e)

                try: 
                    object_is_reply = activity.reply != None
                except Exception as e: 
                    print(e)
                    
                if object_is_poll: 
                    poll_dictt = compile_poll_details(request, activity, request.user)
                    dictt['l_and_s'].append(poll_dictt)


            if source == Like: 
                try:
                    object_is_poll = activity.poll != None
                except Exception as e:
                    print(e)

                try:
                    object_is_opinion = activity.opinion != None

                except Exception as e:
                    print(e)

                try:
                    object_is_comment = activity.comment != None
                except Exception as e:
                    print(e)

                try: 
                    object_is_reply = activity.reply != None
                except Exception as e: 
                    print(e)       


                if object_is_poll:
                    activity = activity.poll 
                    poll_dictt = compile_poll_details(request, activity, request.user)
                    dictt['l_and_s'].append(poll_dictt)         

    return dictt
    


@view_config(route_name='get_posts', renderer='json')
def get_posts(request):
    dictt = {'opinions': []}
    user_id = request.matchdict.get('user_id', None)
    if user_id:
        user = request.dbsession.query(User).filter(User.id == user_id).first()
        for opinion in user.opinions:
            op_dictt = compile_opinion_details(request, opinion, request.user)
            dictt['opinions'].append(op_dictt)
    return dictt


@view_config(route_name='get_slug', renderer='json')
def get_slug(request):
    user_id = request.matchdict.get('user_id', None)
    user = request.dbsession.query(User).filter(User.id == user_id).first()

    user_slug = user.slug

    return {'userSlug': user_slug}