class Poll:
    def __init__(self, *args, **kwargs):
        poll_id = kwargs.get('poll_id', None)
        poll_title = kwargs.get('poll_title', None)
        poll_poser = kwargs.get('poll_poser', None)
        target_age = kwargs.get('target_age', None)
        target_category = kwargs.get('target_category', None)
        target_location = kwargs.get('target_location', None)
        target_profession = kwargs.get('target_profession', None)

        
        if poll_id: 
            self.poll_id = poll_id
            
        if poll_title:
            self.poll_title = poll_title

        if poll_poser:
            self.poll_poser = poll_poser

        if target_age:
            self.target_age = target_age

        if target_category:
            self.target_category = target_category

        if target_location:
            self.target_location = target_location

        if target_profession:
            self.target_profession = target_profession

        self.post_title = post_title
        self.poster = user_name
        self.target_age = target_age
        self.target_location = target_location
 
    @property
    def location(self):
        return self.target_location
    
    @property
    def age(self):
        return self.target_age


class UserDetails:
    pass 


class Ranker:

    def __init__(self, user_location, user_age, posts):
        self.user_location = user_location
        self.user_age = user_age
        self.posts = posts
        self.user_followers = []
        self.ranked_posts = {}
        self.relevant_posts = []
    
    def rank(self):
        for post in self.posts:
            same_age = 1 if post.target_age == self.user_age else 0
            same_location = 2 if post.target_location == self.user_location else 0
            from_follower = 3 if post.poster in self.user_followers else 1

            result = same_age * same_location * from_follower

            self.ranked_posts[str(post.post_id)] = result
            

    def _set_relevant_posts(self):
        for k, v in self.ranked_posts.items():
            if v is not 0:
                self.relevant_posts.append(k)


    def get_ranked_posts(self):
        return self.ranked_posts

    def _get_relevant_posts(self):
        self._set_relevant_posts()
        return self.relevant_posts

    def get_scored_posts(self):
        return sorted(self.relevant_posts)
   
