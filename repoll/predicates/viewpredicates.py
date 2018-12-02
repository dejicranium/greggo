class IfUserAgentPredicate: 
	def __init__(self, val, config):
		self.val = val

	def text(self):
		return "user_agent = {}".format(self.val)

	phash = text

	def __call__(self, context, request):
		import re
		is_mobile = None
		if re.search('mobi', request.user_agent, re.IGNORECASE) is not None:
			is_mobile = True
		return is_mobile == True and self.val == 'mobile'