from ..models.main_models import *
from .activity_service import get_source
import random
from ..utils.scraper_util import get_first_url, url_exists, get_page_thumb_title_desc, get_page_desc, get_page_thumb
from ..utils.compile_util import (
                                    return_polls_voted_in, 
                                    return_opinions_voted_in, 
                                    compile_comment_details,
                                    compile_reply_details
)
from greggo.storage.redis.trending_storage import *
from greggo.storage.redis.user_followings_storage import FollowingsManager
from .metrics_service import *
from .activity_service import get_latest_activities

def user_is_following( user1_id, user2_id):
    return FollowingsManager.user_is_following(user1_id, user2_id)

def return_polls_results_seen_by_user(request, user):
    seen_results = []
    for poll in user.polls_seen_results:
        seen_results.append(int(poll.poll_id))

    return seen_results



def get_activities_if_authenticated(request, user, already_shown):

    from greggo.feed_managers.base import FeedManager

    user_full_name = user.full_name
    user_pic = user.profile_picture
    dictt = {'user_logged_in': True, 'userName': user_full_name, 'userPic': user_pic, 'activities': []}

    # get activities
    #activities = request.dbsession.query(Activity)
    user_categories = []
	
    for each in user.subscriptions: 
        categories = request.dbsession.query(Category).filter_by(id=each.category_id).all()
        for category in categories:
            user_categories.append(category.id)

    
    activities = FeedManager(user.id).get_all_feeds(user_categories)

    
    #activities = get_latest_activities(request, user.id, already_shown)
    activities = request.dbsession.query(Activity).filter(Activity.id.in_(activities)).all() 
    
    #activities = random.sample(set(activities), len(activities))
    activities = activities[::-1]

    for activity in activities:
        source = get_source(request, activity)
        source_id = activity.source_id

        a = request.dbsession.query(source).filter(source.id == source_id).first()
        if source == Poll:
            option_votes = [option.votes for option in a.options]
            poll_has_url_in_info = url_exists(a.info)

            # this is to check whether any option has an image attached to it. Normally, every option should
            # have an image in a picture poll
            options_with_image = [option for option in a.options if option.image_link is not None]
            poll_dictt = {
                'type': 'poll',
                'id': a.id,
                'userId': a.added_by.id,
                'userName': a.added_by.full_name,
                'userInitials': a.added_by.initials,
                'userPic': a.added_by.profile_picture,
                'userSlug': a.added_by.slug,
                'imageInfo': a.info_image_link,
                'question': a.question,
                'info': a.info,
                'totalVotes': a.num_of_votes,
                'slug': a.slug,
                'timeAdded': a.time_added,
                'isPicturePoll': options_with_image != [],  #
                'hasUrlInInfo': url_exists(a.info),
                'infoPageThumb': a.info_link_thumb,
                'infoPageTitle': a.info_link_title,
                'infoPageDescription': a.info_link_desc,
                'userHasVoted': a.id in return_polls_voted_in(request, user) or a.poser == request.user.id,
                'userHasSeenResults': a.id in return_polls_results_seen_by_user(request, user),
                'hasEnded': a.has_ended,
                'timeRemaining': a.time_remaining,
                'numOfLikes': a.num_of_likes,
                'userHasLiked': request.user.id in [like.user_id for like in a.likes],
                'userIsFollowing': True if request.user.id == a.added_by.id else user_is_following(request.user.id, a.added_by.id),
                'numOfComments': a.num_of_comments, 
                'options': [
                    {
                        'id': option.id,
                        'option': option.title,
                        'image': option.image_link,
                        'score': 0 if not option.num_of_votes else option.num_of_votes,

                    } for option in a.options],

            }

            dictt['activities'].append(poll_dictt)









        elif source == Comment:
            object_is_poll = None
            object_is_opinion = None
            try:
                object_is_poll = a.poll
            except:
                print('nothin')

            try:
                object_is_opinion = a.opinion
            except:
                print('nothing')

            comment_dictt = {
                'type': 'comment',
                'id': a.id,
                'userId': a.added_by.id,
                'commenterInitals': a.added_by.initials,
                'commenter': a.added_by.full_name,
                'comment': a.comment,
                'numOfReplies': a.num_of_replies,
                'option_chosen': a.option.title,
                'userIsFollowing': user_is_following(request.user.id, a.added_by.id),
                
                # 'opinion': {'userName': a.opinion.added_by.full_name,
                #			'opinion': a.opinio
                #	a.opinion.opinion if object_is_opinion else None}
            }

            if object_is_poll:
                comment_dictt['poll'] = {
                    'userName': a.poll.added_by.full_name,
                    'question': a.poll.question,
                    'slug': a.poll.slug,
                    'timeAdded': a.poll.time_added,

                }
            if object_is_opinion:
                comment_dictt['opinion'] = {
                    'userName': a.opinion.added_by.full_name,
                    'opinion': a.opinion.opinion,
                    'timeAdded': a.opinion.time_added,
                }
            dictt['activities'].append(comment_dictt)




        elif source == Opinion:
            opinion_dictt = {

                'id': a.id,
                'type': 'opinion',
                'userId': a.added_by.id,
                'userName': a.added_by.full_name,
                'userPic': a.added_by.profile_picture,
                'opinion': a.opinion,
                'options': [
                    {
                        'id': option.id,
                        'option': option.title,
                        'score': 0 if not option.num_of_votes else option.num_of_votes,

                    } for option in a.options],
                'totalVotes': a.num_of_votes,
                'numOfComments': a.num_of_comments,
                'numOfShares': a.num_of_shares,
                'numOfLikes': a.num_of_likes,
                'timeAdded': a.time_added,
                'userHasVoted': a.id in return_opinions_voted_in(request, user) or a.user_id == request.user.id,
                'userIsFollowing': user_is_following(request.user.id, a.added_by.id),
                'contextImage': [
                    {'imgLink': img.image_link} for img in a.context_images
                    ]
                }
            

            dictt['activities'].append(opinion_dictt)













        elif source == Like:
            object_is_poll = None
            object_is_opinion = None
            object_is_comment = None
            object_is_reply = None
            try:
                object_is_poll = a.poll
            except:
                print("nothing")

            try:
                object_is_opinion = a.opinion != None
            except:
                print('nothing')
            try:
                object_is_reply = a.reply != None
            except:
                print('nothing')
            try:
                object_is_comment = a.comment != None
            except:
                print('nothing')

            if object_is_poll:
                options_with_image = [option for option in a.poll.options if option.image_link is not None]
                poll_dictt = {
                    'trigger': 'liked',
                    'triggerActor': a.added_by.full_name,
                    'type': 'poll',
                    'id': a.poll.id,
                    'userName': a.poll.added_by.full_name,
                    'userInitials': a.poll.added_by.initials,
                    'userPic': a.poll.added_by.profile_picture,
                    'imageInfo': a.poll.info_image_link,
                    'question': a.poll.question,
                    'info': a.poll.info,
                    'totalVotes': a.poll.num_of_votes,
                    'slug': a.poll.slug,
                    'isPicturePoll': options_with_image != [],  #
                    'hasUrlInInfo': url_exists(a.poll.info),
                    'infoPageThumb': a.poll.info_link_thumb,
                    'infoPageTitle': a.poll.info_link_title,
                    'infoPageDescription': a.poll.info_link_desc,
                    'userHasVoted': a.poll.id in return_polls_voted_in(request, user) or request.user.id == a.poll.poser,
                    'userHasSeenResults': a.poll.id in return_polls_results_seen_by_user(request, user),
                    'hasEnded': a.poll.has_ended,
                    'userIsFollowing': user_is_following(request.user.id, a.poll.id),
                    'timeRemaining': a.poll.time_remaining,
                    'timeAdded': a.poll.time_added,
                    'userHasLiked': request.user.id in [like.user_id for like in a.poll.likes],
                    'numOfLikes': a.poll.num_of_likes,
                    'options': [
                        {
                            'id': option.id,
                            'option': option.title,
                            'image': option.image_link,
                            'score': 0 if not option.num_of_votes else option.num_of_votes,

                        } for option in a.poll.options],
                    'numOfComment': a.poll.num_of_comments,

                }

                dictt['activities'].append(poll_dictt)

            elif object_is_opinion:
                opinion_dictt = {
                    'trigger': 'liked',
                    'triggerActor': a.opinion.added_by.full_name,
                    'id': a.opinion.id,
                    'type': 'opinion',
                    'userId': a.opinion.added_by.full_name,
                    'opinion': a.opinion.opinion,
                    'options': [
                        {
                            'id': option.id,
                            'option': option.title,
                            'score': 0 if not option.num_of_votes else option.num_of_votes,

                        } for option in a.opinion.options],
                    'numOfVotes': a.opinion.num_of_votes,
                    'numOfComments': a.opinion.num_of_comments,
                    'numOfShares': a.opinion.num_of_shares,
                    'numOfLikes': a.opinion.num_of_likes,
                    'userIsFollowing': user_is_following(request.user.id, a.opinion.added_by.id),
                }
                dictt['activities'].append(opinion_dictt)

            elif object_is_comment:
                comment_dictt = {
                    'type': 'comment',
                    'comment_id': a.id,
                    'userId': a.added_by.id,
                    'commenterInitals': a.added_by.initials,
                    'commenter': a.added_by.full_name,
                    'comment': a.comment,
                    'option_chosen': a.option.title,
		            'userHasLiked': request.user.id in [like.user_id for like in comment.likes],
                    # 'opinion': {'userName': a.opinion.added_by.full_name,
                    #			'opinion': a.opinio
                    #	a.opinion.opinion if object_is_opinion else None}
                    'userIsFollowing': user_is_following(request.user_id, a.added_by.id),
                }
                dictt['activities'].append(comment_dictt)





        elif source == Share:
            object_is_poll = a.poll != None
            object_is_opinion = a.opinion != None
            object_is_reply = a.reply != None
            object_is_comment = a.comment != None

            if object_is_poll:
                options_with_image = [option for option in a.poll.options if option.image_link is not None]
                poll_dictt = {
                    'trigger': 'shared',
                    'triggerActor': a.poll.added_by.full_name,
                    'type': 'poll',
                    'id': a.poll.id,
                    'userName': a.poll.added_by.full_name,
                    'userInitials': a.poll.added_by.initials,
                    'userPic': a.poll.added_by.profile_picture,
                    'imageInfo': a.poll.info_image_link,
                    'question': a.poll.question,
                    'info': a.poll.info,
                    'totalVotes': a.poll.num_of_votes,
                    'slug': a.poll.slug,
                    'isPicturePoll': options_with_image != [],  #
                    'hasUrlInInfo': url_exists(a.poll.info),
                    'infoPageThumb': a.poll.info_link_thumb,
                    'infoPageTitle': a.poll.info_link_title,
                    'infoPageDescription': a.poll.info_link_desc,
                    'userHasVoted': a.poll.id in return_polls_voted_in(request, user),
                    'userHasSeenResults': a.poll.id in return_polls_results_seen_by_user(request, user),
                    'hasEnded': poll.has_ended,
                    'timeRemaining': poll.time_remaining,
                    'numOfComments': poll.num_of_comments,
                    'options': [
                        {
                            'id': option.id,
                            'option': option.title,
                            'image': option.image_link,
                            'score': 0 if not option.num_of_votes else option.num_of_votes,

                        } for option in a.poll.options],

                }

                dictt['activities'].append(poll_dictt)

            elif object_is_opinion:
                opinion_dictt = {
                    'trigger': 'shared',
                    'triggerActor': a.opinion.added_by.full_name,
                    'id': a.opinion.id,
                    'type': 'opinion',
                    'userId': a.opinion.added_by.full_name,
                    'opinion': a.opinion.opinion,
                    'options': [
                        {
                            'id': option.id,
                            'option': option.title,
                            'score': 0 if not option.num_of_votes else option.num_of_votes,

                        } for option in a.opinion.options],
                    'numOfVotes': a.opinion.num_of_votes,
                    'numOfComments': a.opinion.num_of_comments,
                    'numOfShares': a.opinion.num_of_shares,
                    'numOfLikes': a.opinion.num_of_likes,
                }
                dictt['activities'].append(opinion_dictt)

            elif object_is_comment:
                comment_dictt = compile_comment_details(request, a.comment, user)
                comment_dictt['trigger'] = 'shared'
                comment_dictt['triggerActor'] = a.comment.added_by.full_name


                dictt['activities'].append(comment_dictt)

    #			like_dictt = {
    #				'id': a.id,
    #				'type': 'like',
    #				'userId': a.added_by.full_name,
    #				'poll': {'userId': a.poll.added_by.full_name,
    #						'question': a.poll.question} if object_is_poll else None,
    #
    #				 'opinion': {'userId': a.opinion.added_by.full_name,
    #				 			'opinion': a.opinion.opinion} if object_is_opinion else None,
    #
    #	}
    #    dictt['activities'].append(like_dictt)

        elif source == Reply:
            reply_dictt = compile_reply_details(request, a, user)
            dictt['activities'].append(reply_dictt)


    return dictt





















def choose_random_demographic_insight(request, poll_id):
    poll = request.dbsession.query(Poll).filter(Poll.id == poll_id).first()
    poll_options_ids = [option.id for option in poll.options]

    ages = [15, 18, 21, 20, 25, 25, 30, 35]
    demographic_insight = ['gender', 'age_range']

    chosen_demographic_object = random.sample(demographic_insight, 1)
    chosen_demographic_object = "".join(chosen_demographic_object)

    chosen_option_id = (random.sample(poll_options_ids, 1))
    chosen_option_id = str(chosen_option_id[0])
    chosen_option_id = int(chosen_option_id)

    option = request.dbsession.query(Option).filter(Option.id == chosen_option_id).first()

    if chosen_demographic_object == 'gender':
        new_metric_object = MetricsAggregator(chosen_demographic_object, '', 'option', chosen_option_id, poll_id)
        derived_metrics = new_metric_object.get_metrics(PollVotersGenderStorage)
        title = "Sex of voters who voted '{}' in poll: {}".format(option.title, poll.question)
      
        derived_metrics['type'] = 'demo'
        derived_metrics['id'] = poll.id
        derived_metrics['main_focus'] = 'gender'
        derived_metrics['sub_focus'] = 'option'
        derived_metrics['title'] = title

    else:
        lower_bound = random.sample(ages, 1)
        lower_bound = int(str(lower_bound[0]))
        upper_bound = lower_bound + 5
        age_range_string = '{}-{}'.format(lower_bound, upper_bound)
        new_metric_object = MetricsAggregator(chosen_demographic_object, age_range_string, 'options', chosen_option_id, poll_id)
        derived_metrics = new_metric_object.get_metrics(PollVotersAgeStorage)
        
        title = "Users between ages {}-{}, who voted '{}' in poll: {}".format(lower_bound, upper_bound, option.title, poll.question)
        derived_metrics['type'] = 'demo'
        derived_metrics['main_focus'] = 'age_range'
        derived_metrics['sub_focus'] = 'options'
        derived_metrics['title'] = title
        derived_metrics['lowerBound'] = lower_bound
        derived_metrics['upperBound'] = upper_bound

    return derived_metrics




def get_activities_if_not_autheticated(request):
    """This function returns the activities to be shown to a user when they
            they are not logged in.

        The usual activities to be shown are actually trending activities.
        But in the absence or shortage of trending activites, we'd just show recent 
            activities.
    """
    
    act_dictt = {'user_logged_in': False, 'activities': []}

    polls = TrendingPollsStorage().get_polls()
    comments = TrendingCommentsStorage().get_comments()
    opinions = TrendingOpinionsStorage().get_opinions()
    polls = [int(poll_id) for poll_id in polls]
    comments = [int(i) for i in comments]
    opinions = [int(i) for i in opinions]
    

    #for a third of the polls, we are going to the demographic distribution
    import random
    random_polls = random.sample(polls, int(len(polls)/2))


    for poll in random_polls: 
        act_dictt['activities'].append(choose_random_demographic_insight(request, poll))


    for poll_id in polls:
        poll = request.dbsession.query(Poll).filter(Poll.id ==poll_id).first()

        poll_dictt = {
            'type': 'poll',
            'id': poll.id,
            'userId': poll.added_by.id,
            'userName': poll.added_by.full_name,
            'userPic': poll.added_by.profile_picture,
            'imageInfo': poll.info_image_link,
            'question': poll.question,
            'info': poll.info,
            'totalVotes': poll.num_of_votes,
            'slug': poll.slug,
            'timeAdded': poll.time_added,
            'hasUrlInInfo': url_exists(poll.info),
            'infoPageThumb': poll.info_link_thumb,
            'infoPageTitle': poll.info_link_title,
            'infoPageDescription': poll.info_link_desc,
            'userHasVoted': False,
            'hasEnded': poll.has_ended,
            'options': [
                {
                    'id': option.id,
                    'image': option.image_link,
                    'option': option.title,
                    'score': 0 if not option.num_of_votes else option.num_of_votes
                } for option in poll.options
            ],

        }

        act_dictt['activities'].append(poll_dictt)

    for comment_id in comments:
        comment = request.dbsession.query(Comment).filter(Comment.id ==comment_id).first()
        try:
            object_is_poll = comment.poll != None
        except:
            print("Nothing")
        try:
            object_is_opinion = comment.opinion != None
        except:
            print("Nothing")

        comment_dictt = {
            'type': 'comment',
            'userId': comment.added_by.id,
            'comment_id': comment.id,
            'commenterInitals': comment.added_by.initials,
            'commenter': comment.added_by.full_name,
            'comment': comment.comment,
            'option_chosen': comment.option.title,
            'opinion': comment.opinion.opinion if object_is_opinion else None
        }

        if object_is_poll:
            comment_dictt['poll'] = {
                    'userName': comment.poll.added_by.full_name,
                    'question': comment.poll.question,
                    'slug': comment.poll.slug,
                    'timeAdded': comment.poll.time_added,

            }
        elif object_is_opinion:
            comment_dictt['opinion'] = {
                    'userName': a.opinion.added_by.full_name,
                    'opinion': a.opinion.opinion,
                    'timeAdded': a.opinion.time_added,
            }        
            
        act_dictt['activities'].append(comment_dictt)

   # for opinion_id in opinions:
    #    opinion = request.dbsession.query(Opinion).filter(Opinion.id == opinion_id).first()
    #    opinion_dictt = {

     #       'id': opinion.id,
     #       'type': 'opinion',
     ##       'userId': opinion.added_by.full_name,
     #       'userPic': opinion.added_by.profile_picture,
    #        'opinion': opinion.opinion,
    #        'timeAdded': opinion.time_added,
     #       'options': [
     #           {
     #               'id': option.id,
    #                'option': option.title,
   #                 'score': 0 if not option.num_of_votes else option.num_of_votes,

    #            } for option in opinion.options],
     #       'numOfVotes': opinion.num_of_votes,
     #       'numOfComments': opinion.num_of_comments,
     #       'numOfShares': opinion.num_of_shares,
      #      'numOfLikes': opinion.num_of_likes,
       # }

        #act_dictt['activities'].append(opinion_dictt)

    return act_dictt
