class GiveAway:
    user_id = 100000
    def __init__(self, user_id):
        self.user_id = user_id

    @classmethod
    def give_gifts(cls):
        return cls.user_id
