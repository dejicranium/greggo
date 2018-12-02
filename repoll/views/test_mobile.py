from ..models.main_models import *
from pyramid.view import view_config
from ..services.feed_service import (
									return_polls_voted_in, 
									get_activities_if_authenticated,
									get_activities_if_not_autheticated
									)
import random

from greggo.storage.redis.trending_storage import *
from repoll.utils.compile_util import *


@view_config(route_name='mobile_feed', renderer='../templates/test_mobile.jinja2')
def home_feed(request):

	if request.user:
		user = request.dbsession.query(User).filter(User.id==request.user.id).first()
		return {'er': '', 'user': user}
	return {'user': False}



@view_config(route_name='get_latest_posts', renderer='json')
def get_activities(request):
	already_shown = []

	try:
		already_shown = request.json_body.get('already_shown')
		already_shown = already_shown.split(',')
	except:
		pass

	
	if request.user:
		
		user = request.dbsession.query(User).filter(User.id==request.user.id).first()
		request.response.headers.update({
			'Access-Control-Allow-Origin': '*',
		})
		activities = get_activities_if_authenticated(request, user, already_shown)

		return activities
	else: 
		return get_activities_if_not_autheticated(request)



@view_config(route_name='trending_page', renderer='../templates/trending_mobile_page.jinja2')
def trending_page(request):
	if request.user:
		user = request.dbsession.query(User).filter(User.id==request.user.id).first()
	else:
		user = False
	return {'er': 'er', 'user': user}
	

@view_config(route_name='get_trending', renderer='json')
def get_trending(request):
	dictt = {'activities': []}
	"""
	polls = TrendingPollsStorage().get_polls()
	for poll in polls:
		poll_id = poll
		poll = request.dbsession.query(Poll).filter(Poll.id==poll_id).first()
		polls.append(poll)

	comments = TrendingCommentsStorage().get_comments()

	opinions = TrendingOpinionsStorage().get_opinions()

	for poll in polls:
		poll_dictt = compile_poll_details(request, poll, request.user)
		dictt['activities'].append(poll_dictt)

	for opinion in opinions: 
		comment_dictt = compile_opinion_details(request, opinion, request.user)
		dictt['activities'].append(poll_dictt)
	"""
	return dictt	
		
