from ..models.main_models import *
from pyramid.view import view_config
from ..services.activity_service import ActivityService
from greggo.storage.redis.trending_storage import TrendingCommentsStorage
import transaction
from ..utils.compile_util import compile_reply_details



def increase_num_of_replies(source_obj, source_class):
    source_obj.update({'num_of_replies': (source_class.num_of_replies + 1)})


@view_config(route_name='reply_to_comment', renderer='json')
def reply_to_comment(request):
    try:
        body = request.json_body 
        comment_id = body.get('comment_id', None)
        reply_text = body.get('reply', None)
        user_id = request.user.id

        comment_obj = request.dbsession.query(Comment).filter(Comment.id==comment_id)
        comment = comment_obj.first()
    
        new_reply = Reply(
            reply=reply_text,
            from_user=user_id, 
            to_user=comment.commenter_id,
            comment_id=comment.id,
            conversation_id=comment.conversation_id, 
        )

        
        increase_num_of_replies(comment_obj, Comment)

        request.dbsession.add(new_reply)
        request.dbsession.flush()

        #add to trending comments
        trending_comments = TrendingCommentsStorage()
        trending_comments.add_comment(comment)
        
        #input necessary details into trend

        #create new activity
        new_activity = ActivityService(request, 'reply', request.user, new_reply, comment) 
        new_activity.create_new_activity()

        transaction.commit()
        request.response.status = '200'
        return {'status': 'success'}

    except Exception as e: 
        request.response.status = '400'
        return {'status': e}
    

@view_config(route_name='reply_to_reply', renderer='json')
def reply_to_reply(request):
    try:
        body = request.json_body
        reply_id = body.get('reply_id', None)
        reply_text = body.get('reply', None)
        user_id = request.user.id

        reply_obj = request.dbsession.query(Reply).filter(Reply.id==reply_id)
        reply = reply_obj.first()

        new_reply = Reply(
            reply=reply_text,
            from_user=user_id, 
            to_user=reply.from_user, 
            replied_id=reply_id,
            conversation_id=reply.conversation_id
        )

        #input details in trending

        request.dbsession.add(new_reply)
        request.dbsession.flush()

        increase_num_of_replies(reply_obj, Reply)
    #add activity
        new_activity = ActivityService(request, 'reply', request.user, new_reply, reply)
        new_activity.create_new_activity()

        transaction.commit()
    
        request.response.status = '200'
        return {'status': 'success'}
    except Exception as e:
        request.response.status = '400'
        return {'status': e}



@view_config(route_name='reply_to_opinion', renderer='json')
def reply_to_opinion(request):
    try:
        body = request.json_body
        opinion_id = body.get('opinion_id', None)
        user_id = request.user.id
        reply_text = body.get('reply', None)

        opinion_obj = request.dbsession.query(Opinion).filter(Opinion.id==opinion_id)
        opinion = opinion_obj.first()

        new_reply = Reply(
            reply=reply_text,
            from_user=user_id, 
            to_user=opinion.user_id, 
            opinion_id=opinion_id,
        )

        #input details in trending

        request.dbsession.add(new_reply)
        request.dbsession.flush()

        increase_num_of_replies(opinion_obj, Opinion)
    #add activity
        new_activity = ActivityService(request, 'reply', request.user, new_reply, opinion)
        new_activity.create_new_activity()

        transaction.commit()
    
        request.response.status = '200'
        return {'status': 'success'}
    except:
        request.response.status = '400'
        return {'status': 'failed'}




@view_config(route_name='delete_reply', renderer='json')
def delete_reply(request):
    body = request.json_body
    reply_id = request.matchdict.get('reply_id', None)

    #delete reply
    request.dbsession.query(Reply).filter(Reply.id==reply_id).delete()
    request.dbsession.query(Activity).filter(Activity.source_id==reply_id).delete()
    
    transaction.commit()




@view_config(route_name='get_comment_replies', renderer='json')
def get_comment_replies(request): 
    reply_dictt = {'replies': []}
    user = None
    if request.user:
        user = request.dbsession.query(User).filter(User.id==request.user.id).first()
    comment_id = request.matchdict.get('comment_id', None)
    comment = request.dbsession.query(Comment).filter(Comment.id==comment_id).first()

    replies = comment.replies

    for reply in replies:
        dictt = compile_reply_details(request, reply, user)
        reply_dictt['replies'].append(dictt)

    return reply_dictt

@view_config(route_name='get_reply_replies', renderer='json')
def get_reply_replies(request):
    reply_dictt = {'replies': []}
    user = None
    if request.user:
        user = request.dbsession.query(User).filter(User.id==request.user.id).first()
    reply_id = request.matchdict.get('reply_id', None)
    reply = request.dbsession.query(Reply).filter(Reply.id==reply_id).first()

    replies = reply.replies

    for reply in replies:
        dictt = compile_reply_details(request, reply, user, recursive_replies=True)
        reply_dictt['replies'].append(dictt)

    return reply_dictt