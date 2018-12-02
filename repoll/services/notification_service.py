from repoll.models.main_models import *

class NotificationService: 
    
    def __init__(self, request, user_id, sender_id, activity_type, source, act_object=None):
        self.user_id = user_id 
        self.request = request
        self.source = source
        self.object = act_object

        if isinstance(self.source, Poll):
            source = self.source
            self.source_type = 'poll'
            self.source_id = source.id
            
            
        elif isinstance(self.source, Following):
            self.source_type = 'follow'
            self.source_id = self.source.id
           
        elif isinstance(self.source, PollVotes):
            self.source_type ='poll_vote'
            self.source_id = self.source.id 

        elif isinstance(self.source, OpinionVotes):
            self.source_type ='opinion_vote'
            self.source_id = self.source.id 

        elif isinstance(self.source, Comment):
            self.source_type = 'comment'
            self.source_id = self.source.id
        
        elif isinstance(self.source, Agrees):
            self.source_type = 'agree'
            self.source_id = self.source.id
        
        elif isinstance(self.source, Like):
            self.source_type = 'like'
            self.source_id = self.source.id
        
        elif isinstance(self.source, Share):
            self.source_type = 'share'
            self.source_id = self.source.id
        
        elif isinstance(self.source, Opinion):
            self.source_type = 'opinion'
            self.source_id = self.source.id

        if self.object:
            self.object_id = self.object.id
            
            if isinstance(self.object, Poll):
                self.object_type = 'poll'
            elif isinstance(self.source, Following) and isinstance(self.object, User):
                self.object_type = 'follow'

            elif isinstance(self.object, Comment):
                self.object_type = 'comment'
            
            elif isinstance(self.object, Agrees):
                self.object_type = 'agree'
            
            elif isinstance(self.object, Like):
                self.object_type = 'like'
            
            elif isinstance(self.object, Share):
                self.object_type = 'share'
            
            elif isinstance(self.object, Opinion):
                self.object_type = 'opinion'

            elif isinstance(self.object, Vote):
                self.object_type = 'vote'

        self.sender_id = sender_id


        if activity_type == 'poll':
            self.action_type = 'created'
        elif activity_type == 'opinion':
            self.action_type = 'posted'
        
        elif activity_type == 'like':
            self.action_type = 'liked'
        
        elif activity_type == 'poll_vote' or activity_type =='opinion_vote':
            self.action_type = 'voted on'
        
        elif activity_type == 'comment':
            self.action_type = 'commented on'
        
        elif activity_type == 'follow':
            self.action_type = 'followed'

        elif activity_type == 'reply':
            self.action_type = 'replied to'

        elif activity_type == 'agree':
            self.action_type = 'agreed with'
        
        elif activity_type == 'share':
            self.action_type = 'shared'

        
    def create_new_notification(self):
        notification =  Notification()
        notification.user_id = self.user_id
        notification.action_type = self.action_type
        notification.sender_id = self.sender_id
        notification.source_type = self.source_type
        notification.source_id = self.source_id
        if self.object_id:
            notification.object_type = self.object_type
            notification.object_id = self.object_id
        
        self.request.dbsession.add(notification)


class Notif:
    def get_unseen_notifications(request, user):
        notifs = request.dbsession.query(Notification).query(Notification.status =='unseen')

    def get_seen_notifications(request, user):
        notifs = request.dbsession.query(Notification).query(Notification.status=='seen')

    def get_read_notifications(request, user):
        notifs = request.dbsession.query(Notification).query(Notification.status=='read')


    def get_latest_notifications(request, user):
        pass

    def aggregate_notifications(notifs):
        user = self.user
        notif_objects = [notif.object_id for notif in notifs]
        unique_notif_objects = set(notif_objects)
        reviewed_notifs = []
        reviewed_notifs = {}
        notifs = None

