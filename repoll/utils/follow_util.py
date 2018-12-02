from ..models.main_models import User

class FollowService:
	@staticmethod
	def follow_user(request, follower, followed):
		following = F