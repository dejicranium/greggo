from pyramid.view import view_config
from ..models.main_models import *
from ..utils.compile_util import compile_poll_details
from greggo.storage.redis.category_subscription import *

def user_is_subscribed(user, category_id):
	user_is_subscribed = False
	for subscription in user.subscriptions: 
		if subscription.category_id == category_id:
			user_is_subscribed = True
			break

	return user_is_subscribed

@view_config(route_name='subscribe_to_category', renderer='json')
def subscribe_to_category(request):
	category_id = request.matchdict.get('category_id', -1)
	user_id = request.user.id

	new_subscription = CategorySubscriber(category_id=category_id, user_id=user_id)
	
	redis_category_subscription = CategorySubscription(category_id)
	redis_category_subscription.add_subscriber(request.user.id)
	
	request.dbsession.add(new_subscription)
	return {"state": "success"}


@view_config(route_name='show_subscriptions', renderer='json')
def show_subscriptions(request):
	
	
	user_id = request.user.id
	#get logged in user
	user = request.dbsession.query(User).filter(User.id==user_id).first()

	subscriptions_dictt = {'subscriptions': []}
	
	#loop through list of subscriptions as seen in CategorySubscriber
	
	for each in user.subscriptions: 
		categories = request.dbsession.query(Category).filter_by(id=each.category_id).all()
		for category in categories:
			dictt = {}
			dictt['categoryId'] = category.id
			dictt['categoryName'] = category.category_name
			subscriptions_dictt['subscriptions'].append(dictt)

	return subscriptions_dictt		


@view_config(route_name='show_categories', renderer='../templates/show_categories.jinja2')
def show_categories(request):
	categories = request.dbsession.query(Category)
	return {'categories': categories}


@view_config(route_name='show_subscribers', renderer='json')
def show_subscribers(request):
	dictt = {}
	category_id = request.matchdict.get('category_id', -1)
	category = request.dbsession.query(Category).filter(Category.id==category_id).first()	
	
	for each in category.subscribers:
		dictt[category.category_name] = each.subscribers.age
	
	return dictt


@view_config(route_name='get_polls_from_category', renderer='json')
def get_polls_from_category(request):
	from repoll.utils.compile_util import compile_poll_details
	category_polls = {'activities': []}
	
	category_id = request.matchdict.get('category_id', None)

	user = request.user


	
	polls = request.dbsession.query(PollCategory).filter(PollCategory.category_id==category_id)

	for p in polls:
		poll = request.dbsession.query(Poll).filter(Poll.id==p.poll_id).first()
		poll_dictt = compile_poll_details(request, poll, user)
		category_polls['activities'].append(poll_dictt)
	return category_polls

@view_config(route_name="category_polls_page", renderer='../templates/category_page.jinja2')
def category_polls_page(request):
	category_id= request.matchdict.get('category_id')
	category = request.dbsession.query(Category).filter(Category.id==category_id).first()
	if request.user:
		user = request.dbsession.query(User).filter(User.id==request.user.id).first()
		subscribed = user_is_subscribed(user, category.id)
		return {'user': user, 'category': category, 'user_is_subscribed': subscribed}
	return {'user': None, 'category': category}


