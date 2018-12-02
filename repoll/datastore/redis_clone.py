import ..models.main_models import User

class UserStore: 
	msg_box = {}

class DataStore:

	@classmethod
	def get_users(cls, request):
		users = request.dbsession.query(User)
		return users

	@classmethod
	def push_to_msg_box(cls, request):
		users = get_users(request)
		user_ids = [user.id for user in users]
		for _id in user_ids:
			UserStore.msg_box[_id] = dict()

class Publish:
	@classmethod
	def broadcast(cls, poll):
		for each in UserStore.msg_box:
			UserStore.msg_box[each] = poll.id 
			



