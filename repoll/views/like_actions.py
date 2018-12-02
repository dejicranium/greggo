
from pyramid.view import view_config
from ..models.main_models import *

from pyramid.response import Response
from ..services.activity_service import ActivityService
import transaction
from pyramid.httpexceptions import HTTPFound
from ..services.notification_service import NotificationService
from sqlalchemy import exists
from greggo.storage.redis.trending_storage import *



@view_config(route_name='like', renderer='json')
def like(request):
    body = request.json_body
    poll_id = body.get('poll_id', None)
    reply_id = body.get('reply_id', None)
    comment_id = body.get('comment_id', None)
    opinion_id = body.get('opinion_id', None)
    user_id = request.user.id
    
    new_like = Like()
    new_like.user_id = request.user.id

    if poll_id: 
        poll_obj = request.dbsession.query(Poll).filter(Poll.id==poll_id)
        poll = poll_obj.first()
        
        #check if user has liked poll before
        like = request.dbsession.query(Like).filter(Like.user_id==user_id, Like.poll_id==poll.id).first()
        if like:
            return {'status': 'already likeds'}


        new_like.user_id = request.user.id
        new_like.poll_id = poll_id
        request.dbsession.add(new_like)
        
        request.dbsession.flush()

        poll_obj.update({'num_of_likes': (Poll.num_of_likes + 1)})
        
        new_activity = ActivityService(request, 'like', request.user, new_like, poll)
        new_activity.create_new_activity()



        activity = new_activity.get_activity()
        
        if poll.poser != request.user.id:
        #notification 
            user_id = activity.object_owner_id
            sender_id = new_like.user_id
            activity_type = activity.activity_type
            source = new_like
            _object = poll

            notif = NotificationService(request, user_id, sender_id, activity_type, source, _object)
            notif.create_new_notification()
            transaction.commit()

    
    if comment_id: 
        comment_obj = request.dbsession(Comment).filter(Comment.id==comment_id)
        comment = comment_obj.first()

        new_like.user_id = request.user.id
        new_like.comment_id = comment_id
        request.dbsession.add(new_like)
        request.dbsession.flush()

        comment_obj.update({'num_of_likes': (Comment.num_of_likes + 1)})

        #add to trending comments
        trending_comments = TrendingCommentsStorage()
        trending_comments.add_comment(comment)

        new_activity = ActivityService(request, 'like', request.user, new_like, comment)
        new_activity.create_new_activity()
        transaction.commit()

    if reply_id:
        reply = request.dbsession(Reply).filter(Reply.id==reply_id).first() 
        new_like.reply_id = reply_id
        request.dbsession.add(new_like)
        request.dbsession.flush()

        new_activity = ActivityService(request, 'like', request.user, new_like, reply)
        new_activity.create_new_activity()
        transaction.commit()

    if opinion_id:
        opinion = request.dbsession.query(Opinion).filter(Opinion.id==opinion_id).first()
        new_like.opinion_id = opinion_id
        request.dbsession.add(new_like)
        request.dbsession.flush()
        
        new_activity = ActivityService(request, 'like', request.user, new_like, opinion)
        new_activity.create_new_activity()

        activity = new_activity.get_activity()
        
        #notification 
        user_id = activity.object_owner_id
        sender_id = new_like.user_id
        activity_type = activity.activity_type
        source = new_like
        _object = opinion

        notif = NotificationService(request, user_id, sender_id, activity_type, source, _object)
        notif.create_new_notification()


@view_config(route_name='unlike', renderer='json')
def undo_like(request):
    body = request.json_body
    user_id = request.user.id
    poll_id = body.get('poll_id', None)
    reply_id = body.get('reply_id', None)
    comment_id = body.get('comment_id', None)
    opinion_id = body.get('opinion_id', None)

    if poll_id: 
        try:
            poll = request.dbsession.query(Poll).filter(Poll.id==poll_id)
            like_obj = request.dbsession.query(Like).filter(Like.user_id==user_id, Like.poll_id==poll_id)
            like = like_obj.first()
            if like:

                like_obj.delete()
                like_activity = request.dbsession.query(Activity).filter(Activity.source_id==like.id)
                like_activity.delete()
                poll.update({'num_of_likes': (Poll.num_of_likes - 1)})

                transaction.commit()

        except Exception as e: 
            return {'error': e}
    elif reply_id: 
        try: 
            reply = request.dbsession.query(Reply).filter(Reply.id==reply_id)
            like_obj = request.dbsession.query(Like).filter(Like.user_id == user_id, Like.reply_id==reply_id)
            like = like_obj.first()
            if like:
                like_obj.delete()

                #delete the activity wher_you there is the like

                reply.update({'num_of_likes': (Reply.num_of_likes - 1)})

                transaction.commit()
        except Exception as e: 
            request.response.status = "400"
            return {}
    
    elif comment_id: 
        try: 
            comment = request.dbsession.query(Comment).filter(Comment.id==comment_id)
            like_obj = request.dbsession.query(Like).filter(Like.comment_id==comment_id, Like.user_id==user_id)
            like = like_obj.first()

            if like:
                like_obj.delete()
                like_activity = request.dbsession.query(Activity).filter(Activity.source_id==like.id)
                like_activity.delete()

                comment.update({"num_of_likes": (Comment.num_of_likes - 1)})

                transaction.commit()
        except Exception as e:
            request.response.status = "400"
            return {}
    
    


    