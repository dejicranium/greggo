from ..models.main_models import User
from pyramid.view import view_config


@view_config(route_name='show_users', renderer='json')
def get_all_users(request):
	"""
	users = request.dbsession.query(User)
	user_first_name = [user.slug for user in users]

	return {'users': user_first_name}

	"""
	pass



	#extract details
	
@view_config(route_name='edit_profile', renderer='../templates/edit_profile.jinja2')
def edit_profile(request):
	if request.user:
		if request.method == "GET":
			user_dict = {}
			user_id = request.matchdict.get('user_id', -1)
			if user_id != -1: 
				#if the user who's requesting to edit a profile is the owner of the account
				if request.user.id == user_id:
					user = request.dbsession.query(User).filter(User.id==user_id).first()
					return {'user': user}
				else:
					return {}
			else:
				return {}
		else:
			pass
	else:
		return {}

	
		