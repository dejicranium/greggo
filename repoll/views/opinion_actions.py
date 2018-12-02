from pyramid.view import view_config
from ..models.main_models import (User,
 Poll,
 Option,
 Comment,
 Category,
 PollCategory,
 Activity,
 Vote,
 PollVotes,
 OpinionVotes, 
 SeenResults, 
 Opinion, 
 ContextImage)

from greggo.storage.redis.voters_age_storage import PollVotersAgeStorage, OpinionVotersAgeStorage
from greggo.storage.redis.voters_gender_storage import PollVotersGenderStorage, OpinionVotersGenderStorage
from greggo.storage.redis.trending_storage import TrendingPollsStorage, TrendingOpinionsStorage
from ..services.metrics_service import MetricsAggregator, MetricsObject, DemographObject
from greggo.config import REDIS_SERVER
from repoll.services.notification_service import NotificationService
import datetime
from ..utils.compile_util import return_polls_voted_in, return_opinions_voted_in, return_comments_shared

from ..utils.scraper_util import get_page_thumb_title_desc, url_exists, get_first_url
from pyramid.response import Response
from ..services.activity_service import ActivityService
from ..services.auth_service import add_image_description
from ..form import PollCreateForm
import transaction
from pyramid.httpexceptions import HTTPFound
import uuid
from ..services.auth_service import add_image_description

#@view_config()
@view_config(route_name='create_opinion', renderer='json')
def create_opinion(request):
    options = []
    opinion = request.params.get('opinion') 
    opinion_image = request.params.get('opinion-image', None)

    new_opinion = Opinion()
    new_opinion.opinion = opinion
    new_opinion.user_id = request.user.id
    request.dbsession.add(new_opinion)
    request.dbsession.flush()

    if opinion_image != None:
        if hasattr(opinion_image, 'file'):
            image_file = opinion_image.file
            image_name = "{}".format(uuid.uuid4())
            uploaded_image = add_image_description(image_file, image_name)
            image_link = uploaded_image['secure_url']
            
            context_image = ContextImage()
            context_image.image_link = image_link
            context_image.opinion_id = new_opinion.id
            request.dbsession.add(context_image)

    new_option1= Option()
    new_option1.title = "Agree"
    options.append(new_option1)

    new_option2 = Option()
    new_option2.title = "Disagree"
    options.append(new_option2)


    new_opinion.options = options
    request.dbsession.add(new_opinion)
    request.dbsession.flush()


    #add opinion to trends 
    #trend = TrendingOpinionsStorage()
    #trend.add_opinion(new_opinion)

    new_activity = ActivityService(request, 'opinion', request.user, new_opinion)
    new_activity.create_new_activity()
    transaction.commit()

    return {'opinion': {'id': new_opinion.id, 'options': [{
        'id': option.id, 
        'option': option.title, 
        'score': 0,
        } for option in new_opinion.options]
        }}

#@view_config(route_name='agree_with_opinion', renderer)
@view_config(route_name='opinion_metrics', renderer='../templates/show_opinion_metrics.jinja2')
def get_opinion_metrics(request):
    opinion_id = request.matchdict.get('opinion_id', -1)
    #we need to get details abouthe poll like name and stuff
    opinion = request.dbsession.query(Opinion).filter(Opinion.id==opinion_id).first()
    return {'opinion': opinion}


@view_config(route_name='get_opinion_metrics', renderer='json')
def get_metrics(request):
    main_focus = request.params.get('m_f')
    sub_focus = request.params.get('s_f')
    main_focus_objects = request.params.get('m_f_objs')
    sub_focus_objects = request.params.get('s_f_objs')
    opinion_id = request.matchdict.get('opinion_id')

    #we can't pass a list through the params, so let's get the sub
    # the sub_focus_object when it is options
    if sub_focus_objects == 'options':
        opinion = request.dbsession.query(Opinion).filter(Opinion.id==opinion_id).first()
        sub_focus_objects = [option.id for option in opinion.options]
    else:
        if main_focus == 'age_range':
            sub_focus_objects = sub_focus_objects
        else:
            sub_focus_objects = int(sub_focus_objects)
    
    if main_focus and sub_focus and main_focus_objects and sub_focus_objects and opinion_id:
        request.response.status = '200'
    else:
        request.response.status = '400'

    new_metrics = MetricsAggregator(main_focus, main_focus_objects, sub_focus, sub_focus_objects, opinion_id)
    
    store = None
    if main_focus == 'age' or main_focus == 'age_range':
        store = OpinionVotersAgeStorage
    elif main_focus == 'gender':
        store = OpinionVotersGenderStorage
        

    derived_metrics = new_metrics.get_metrics(store)

    return derived_metrics

@view_config(route_name='view_opinion_page', renderer='../templates/view_opinion_mobile.jinja2')
def view_opinion_page(request):
    opinion_id = request.matchdict.get('opinion_id')
    opinion = request.dbsession.query(Opinion).filter(Opinion.id==opinion_id).first()

    return {'opinion_id': opinion_id}    

@view_config(route_name='view_opinion', renderer='json')
def view_opinion(request):
    opinion_id = request.matchdict.get('opinion_id', None)
    opinion = request.dbsession.query(Opinion).filter(Opinion.id==int(opinion_id)).first()
    
    if request.user:
        user  = request.dbsession.query(User).filter(User.id==request.user.id).first()
    
    dictt = {   'id': opinion.id,
                'type': 'opinion',
                'userId': opinion.added_by.id,
                'userName': opinion.added_by.full_name,
                'userPic': opinion.added_by.profile_picture,
                'opinion': opinion.opinion,
                'numOfVotes': opinion.num_of_votes,
                'numOfComments': opinion.num_of_comments,
                'numOfShares': opinion.num_of_shares,
                'numOfLikes': opinion.num_of_likes,
                'timeAdded': opinion.time_added,
                'contextImage': [
                    {'imgLink': img.image_link} for img in opinion.context_images
                    ]
                }
    if request.user:
        dictt['userHasVoted'] = False

    dictt['options'] = [{           
                        'id': option.id,
                        'option': option.title,
                        'score': 0 if not option.num_of_votes else option.num_of_votes,

                    } for option in opinion.options]

    return dictt