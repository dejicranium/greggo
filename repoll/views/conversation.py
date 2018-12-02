from pyramid.view import view_config
from ..models.main_models import *
import transaction
from repoll.utils.compile_util import compile_comment_details, compile_reply_details


@view_config(route_name='view_conversation_page', renderer='../templates/view_conversation_mobile_page.jinja2')
def view_conversation_mobile_page(request):
    conversation_id = request.matchdict.get('conversation_id', None)
    reply_id = request.matchdict.get('reply_id', None)
    user = request.dbsession.query(User).filter(User.id==request.user.id).first()
    conversation = request.dbsession.query(Conversation).filter(Conversation.id==conversation_id).first()

    return {'conversation': conversation, 'user': user, 'reply_id': reply_id}


@view_config(route_name='get_conversation', renderer='json')
def view_conversation(request):
    dictt = {'comment':{}, 'replies': []}
    conversation_id = request.matchdict.get('conversation_id', None)
    
    user = None
    reply_id = request.matchdict.get('reply_id', None)
    conversation  = request.dbsession.query(Conversation).filter(Conversation.id==conversation_id).first()
    reply = request.dbsession.query(Reply).filter(Reply.id==reply_id).first()

    if request.user:
        user = request.dbsession.query(User).filter(User.id==request.user.id).first()
   
    for counter, comment in enumerate(conversation.comments):
        comment_dictt = compile_comment_details(request, comment, user)
        dictt['comment'] = comment_dictt
        break

    #get_reply
    reply_dictt = compile_reply_details(request, reply, user, upward_recursion=True)
    dictt['replies'].append(reply_dictt)
    
    return dictt