from ..services.follow_service import FollowService, User
from pyramid.view import view_config
from greggo.storage.redis.user_followings_storage import FollowingsManager
from greggo.feed.base import *

@view_config(route_name='follow_user', renderer='json')
def follow_user(request):
	user_id = request.user.id
	followed_id = request.matchdict.get('user_id', None)
	if user_id == int(followed_id):
		request.response.status = '400'
		return {'state': "Nice try. But you can't and shouldn't follow yourself"}

	FollowService.follow_user(request, user_id, followed_id)
	
	#store in redis
	FollowingsManager.follow_user(user_id, followed_id)
	
	
	return {'state': 'success'}

@view_config(route_name='unfollow_user', renderer='json')
def unfollow_user(request):
	user_id = request.user.id
	user_to_unfollow_id = request.matchdict.get('user_id', None)

	if user_id and user_to_unfollow_id: 
		try: 
			FollowService.unfollow_user(request, user_id, user_to_unfollow_id)
			return {'status': 'success'}

			#store in redis
			FollowingsManager.unfollow_user(request, user_id, user_to_unfollow_id)
			to_unfollow_activities = request.dbsession.query(Activity).filter(Activity.user_id==user_to_unfollow_id)
			activities_to_unfollow_id = [activity.id for activity in to_unfollow_activities]

			user_feed = UserFeed(request.user.id)
			user_feed.remove_activities(activities_to_unfollow_id)

			
		except Exception as e:
			request.response.status = '500'
			return {'status': 'failed', 'reason': str(e)}
			

	
@view_config(route_name='followings', renderer='json')
def followings(request):
	user = request.dbsession.query(User).filter(User.id==request.user.id).first()
	followings = FollowService.get_following(request, user)
	return {'followings' : followings}


@view_config(route_name="followers", renderer='json')
def get_followers(request):
	all_followers = []
	names = {}
	user = request.dbsession.query(User).filter(User.id==request.user.id).first()
	followers = FollowService.get_followers(request, user)
	return {'followers': followers}

