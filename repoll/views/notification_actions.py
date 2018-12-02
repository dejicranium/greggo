from pyramid.view import view_config
from repoll.models.main_models import *


""" 
    For each notification, there'll be at least 2 leads:
        
"""

def user_followings(request, user_id):
    user = request.dbsession.query(User).filter(User.id==user_id).first()
    followings = user.following
    followings = [user.id for user in followings]
    return followings

@view_config(route_name='get_notifications', renderer='json')
def get_unseen_notifications(request):
    user_id = request.matchdict.get('user_id')
    dictt = {}
    notifications = request.dbsession.query(Notification).filter(Notification.user_id==user_id, Notification.status=="unseen")
    

    for notif in notifications:
        n_object_id = notif.object_id
        n_type = notif.object_type
        n_action = notif.action_type
        n_sender_id = notif.sender_id
        n_actor = notif.triggered_by.full_name
        

        if n_sender_id == request.user.id:
            continue

        if n_object_id not in dictt.keys():
            dictt[n_object_id] = {}
            dictt[n_object_id] = {
                'objectType': n_type,
                'action': n_action,
                'leadingActors': [],
                'otherActors': [],
                
            }

            if n_sender_id in user_followings(request, user_id) and dictt[n_object_id].leadingActors < 3:
                dictt[n_object_id]['leadingActors'].append(n_actor)
            else:
                dictt[n_object_id]['otherActors'].append(n_sender_id)

        else:
            if dictt[n_object_id]['action'] != n_action :
                dictt[n_object_id] = {}
                dictt[n_object_id] = {
                    'objectType': n_type,
                    'action': n_action,
                    'leadingActors': [],
                    'otherActors': [],
                
                }

                if n_sender_id in user_followings(request, user_id) and len(dictt[n_object_id]['leadingActors']) < 3:
                    dictt[n_object_id]['leadingActors'].append(n_actor)
                else:
                    dictt[n_object_id]['otherActors'].append(n_sender_id)
            else:
                if n_sender_id in user_followings(request, user_id) and len(dictt[n_object_id]['leadingActors']) < 3:
                    dictt[n_object_id]['leadingActors'].append(n_actor)
                else:
                    dictt[n_object_id]['otherActors'].append(n_sender_id)
    new = {"notifs": []}


    for item in dictt.keys():
        leading_actors = dictt[item]['leadingActors']
        other_actors = dictt[item]['otherActors']
        notification_type = dictt[item]['action']
        object_type = dictt[item]['objectType']
        notification_text = ""
        

        if len(leading_actors) > 0:
            leading_actors = " , ".join(leading_actors)
            notification_text = leading_actors

        if len(other_actors) > 0:
            if notification_text:
                if len(other_actors) == 1:
                    notification_text += ' and ' + str(len(other_actors)) + 'other person '
                else:
                    notification_text += ' and ' + str(len(other_actors)) + 'others '
            else:
                if len(other_actors) == 1:
                    notification_text = str(len(other_actors)) + ' person '
                else:
                    notification_text= str(len(other_actors)) + ' people '
        if object_type == 'follow':
            notification_text += notification_type + ' you'
        else:
            notification_text += notification_type + ' your ' + object_type

        new['notifs'].append(notification_text)



    return new
        

if __name__ == '__main__':
    x = {"notifs": [{'1':{'action': 'liked'}}]}

    print (x['notifs'].keys())