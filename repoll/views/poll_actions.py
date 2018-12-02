from pyramid.view import view_config
from ..models.main_models import (User,
 Poll,
 Option,
 Comment,
 Category,
 PollCategory,
 Activity,
 Vote,
 PollVotes, 
 SeenResults)

from greggo.storage.redis.voters_age_storage import PollVotersAgeStorage
from greggo.storage.redis.voters_gender_storage import PollVotersGenderStorage
from greggo.storage.redis.trending_storage import TrendingPollsStorage
from greggo.storage.redis.timeline_storage import RedisCategoryTimelineStorage
from ..services.metrics_service import MetricsAggregator, MetricsObject, DemographObject
from greggo.config import REDIS_SERVER
from repoll.services.notification_service import NotificationService
import datetime

from ..utils.scraper_util import get_page_thumb_title_desc, url_exists, get_first_url
from pyramid.response import Response
from ..services.activity_service import ActivityService
from ..services.auth_service import add_image_description
from ..form import PollCreateForm
import transaction
from pyramid.httpexceptions import HTTPFound
import uuid
from repoll.utils.compile_util import compile_poll_details
from webhelpers2.text import urlify



@view_config(route_name='vote', renderer='json')
def vote(request):
    body = request.json_body
    poll_id = body.get('poll_id')
    option_id = body.get('option_id')

    #get relevant info from db
    user = request.dbsession.query(User).filter(User.id==request.user.id).first()
    option = request.dbsession.query(Option).filter(Option.id == option_id)
    poll = request.dbsession.query(Poll).filter(Poll.id == poll_id)

    new_user_vote = PollVotes()
    new_user_vote.user_id = user.id
    new_user_vote.poll_id = poll_id

    #store the vote
    request.dbsession.add(new_user_vote)
    request.dbsession.flush()

    #increment necessary details 
    poll.update({'num_of_votes' : (Poll.num_of_votes + 1)})   
    option.update({"num_of_votes" : (Option.num_of_votes + 1)})

    #see whether it's trending
    trend_storage = TrendingPollsStorage()
    trend_storage.add_poll(poll.first())

    #save user's age in redis voters age storage
    user_age = user.age
    redis_store = PollVotersAgeStorage(poll_id, REDIS_SERVER)
    redis_store.increment_age(str(user_age) + '::' + str(option_id))

    user_gender = user.sex
    if user.sex:
        redis_store = PollVotersGenderStorage(poll_id, REDIS_SERVER)
        #increment gender_votes
        if user.sex == 'Male':
            redis_store.increment_gender_votes(str('M') + '::' + str(option_id))
        else:
            redis_store.increment_gender_votes(str('F') + '::' + str(option_id))


    activity_service = ActivityService(request, 'poll_vote', request.user, new_user_vote, poll.first())
    activity_service.create_new_activity()
    
    activity = activity_service.get_activity()

    user_id = activity.object_owner_id
    sender_id = new_user_vote.user_id
    activity_type = activity.activity_type
    source = new_user_vote
    _object =  poll.first()

    notif = NotificationService(request, user_id, sender_id, activity_type, source, _object)
    notif.create_new_notification()
    transaction.commit()


    #create a notification

    transaction.commit()

    response = Response
    response.status = '200 0K'
    return {'poll_id': poll_id, 'option_id': option_id}
    




"""
    if request.method == 'POST':
        option = request.POST.get('option')   #returns the value of the option form (integer)
        if not option:                     #if no option was chosen
            return {}

        user_id = request.user.id
        poll_id = request.matchdict.get('poll_id', -1)

        if user_has_voted(request, user_id, poll_id):   //if the user has already voted
                                                            //in this poll
            return {}
    

        new_vote = Vote(poll_id=poll_id, option_id=option, voter_id=user_id)

        request.dbsession.add(new_vote)



        transaction.commit()

        return HTTPFound(location=request.route_url('home'))
"""
"""
@view_config(route_name='create_question', renderer='../templates/create_question.jinja2')
def create_question(request):
    poll_form = PollCreateForm(request.POST)
    options = request.params.getall('option')
    
    question = poll_form.question.data
    info = poll_form.info.data

    if request.user: 
        if request.method == 'POST':
            create_poll.delay(request.dbsession, request.user.id, question, info, options)
            

            return(HTTPFound(location=request.route_url('mobile_feed')))
        
        else:
            return {'form': poll_form}
    else: 
        pass    
    


"""

@view_config(route_name='create_question', renderer='json')
def create_poll(request):
    body = request.params
    question =  body.get('question', None)
    poser = request.user.id
    info = body.get('info', None)
    options = body.get('options', None)

    option_images = body.getall('optionImage')
    option_image_titles = body.getall('option')

    duration = body.get('timeDue', None)
    categories = body.get('categories', None)
    context_image = body.get('context-image', None)


    options_list = []
    poll_categories_list = []

    if categories: 
        categories = categories.split(',')
    if options:
        options = options.split(',')

    
    new_poll = Poll()
    new_poll.poser = poser
    if not question:
        request.response.status = '500'
        return 00
    new_poll.question = question
    new_poll.info = info
    slug = urlify(question)
    #new_poll.slug = slug

    try:
        if context_image != None:
            image_file = context_image.file
            image_name = "{}".format(uuid.uuid4())
            uploaded_image = add_image_description(image_file, image_name)

            new_poll.info_image_link = uploaded_image['secure_url']
    except:
        print("noting")
    if duration: 
        now = datetime.datetime.utcnow()
        year = now.year
        day = now.day + int(duration)
        month = now.month
        hour = now.hour
        minute = now.minute
        second = now.second
        microsecond = now.microsecond
        try:
            new_poll.end_time = datetime.datetime(year, month, day, hour, minute, second, microsecond)
        except:
            day = 1
            month +=1
        finally:
            new_poll.end_time = datetime.datetime(year, month, day, hour, minute, second, microsecond)

    if option_images != None or len(option_images) > 0:
        for i, option_image in enumerate(option_images):
            try:
                try:
                    image_file = option_image.file
                except:
                    request.response.status = '400'
                    return {'eorror':option_image}
                image_name = '{}'.format(uuid.uuid4())
                uploaded_image = add_image_description(image_file, image_name)
                uploaded_image_link = uploaded_image['secure_url']
                    
                new_option = Option()
                new_option.title = option_image_titles[i]
                new_option.image_link  = uploaded_image_link

                options_list.append(new_option)
            except Exception as e:
                request.response.status = '400'
                return {'status': e}
    
    
    if option_image_titles == []:
        for option in options:
            if option != '':
                new_option = Option()
                new_option.title = option
                options_list.append(new_option)

    new_poll.options = options_list
    request.dbsession.add(new_poll)
    request.dbsession.flush()
            

    for category in categories: 
        new_poll_category = PollCategory()
        new_poll_category.poll_id = new_poll.id
        new_poll_category.category_id = int(category)

        category = request.dbsession.query(Category).filter(Category.id== int(category)).first()
        category.polls.append(new_poll_category)

        poll_categories_list.append(new_poll_category)

    #add to redis category

    

    new_poll.categories = poll_categories_list
    request.dbsession.add(*poll_categories_list)
    

    new_activity = ActivityService(request, 'poll', request.user, new_poll)
    new_activity.create_new_activity()
    new_activity = new_activity.get_activity()

    RedisCategoryTimelineStorage.add_to_many(categories, new_activity.id)


    
    transaction.commit()

    return {}

        
"""       
@view_config(route_name='create_question',
    renderer='../templates/create_question.jinja2')
def create_poll(request):
    poll_form = PollCreateForm(request.POST)
    options = request.params.getall('option')
    category_id = request.POST.get('category', -1)
    end_time = request.POST.get('timeDue', -1)
    category = None
    image_info = None

    if category != -1:
        category = request.dbsession.query(Category).filter(Category.id==category_id).first()
    
    option_objs_list =[]
    categories_list = []
    poll_categories = []



    if not request.user:
        return HTTPFound(location=request.route_url('login'))
    
    if request.method == "POST":
        new_poll = Poll()
        new_poll.question = poll_form.question.data
        new_poll.poser = request.user.id
        new_poll.info = poll_form.info.data
        new_time = None

        if end_time != -1:
            import datetime
            now = datetime.datetime.utcnow()
            year = now.year
            month = now.month
            day = now.day + int(end_time)
            minute = now.minute
            hour = now.hour
            second = now.second
            microsecond = now.microsecond
        
        try:
            #you need to make sure you check if this is not the last day of the year too
            new_time = datetime.datetime(year, month, day, hour, minute, second, microsecond)
        except:
            day = 1
            month += 1
            new_time = datetime.datetime(year, month, day, hour, minute, second, microsecond)

        finally:
                
            new_poll.end_time = new_time

        info_has_url = url_exists(new_poll.info)
        if info_has_url:
            url = get_first_url(new_poll.info)
            info_link_thumb, info_link_title, info_link_desc = get_page_thumb_title_desc(url)
            new_poll.info_link_thumb = info_link_thumb
            new_poll.info_link_title = info_link_title
            new_poll.info_link_desc = info_link_desc
        #image_info = request.params.get('image-info', -1)
        #if image_info != -1: 
         #   image_file = image_info.file
           # image_name = "{}.jpg".format(uuid.uuid4())
           # uploaded_image = add_image_description(image_file, image_name)

            #new_poll.info_image_link = uploaded_image['secure_url']
        

        #if targeting, we should show that poll is targeted

        for option in options:
            if option != "":
                new_option = Option()
                new_option.title = option
                option_objs_list.append(new_option)

        new_poll.options = option_objs_list

        if category != "" or category_id != -1 or category_id != None:
            request.dbsession.add(new_poll)
            request.dbsession.flush()

            poll_cat = PollCategory()
            poll_cat.category_id = category.id
            poll_cat.poll_id = new_poll.id
            
            
            poll_categories.append(poll_cat)
            new_poll.categories.append(poll_cat)
            category.polls.append(poll_cat)
            
            request.dbsession.add_all([new_poll, *poll_categories])
            request.dbsession.flush()


            new_activity = ActivityService(request, 'poll', request.user, new_poll)
            new_activity.create_new_activity()
            
            #get activityf details for notification

            transaction.commit()
        else:
            request.dbsession.add(new_poll)
            request.dbsession.flush()
            new_activity = ActivityService(request, 'poll', request.user, new_poll)
            new_activity.create_new_activity()
            transaction.commit()
        
        #question = poll_form.question.data
        #info = poll_form.info.data
        #tasks.create_poll(request, question, info, options).delay()

        return HTTPFound(location=request.route_url('mobile_feed'))

    #we need this for the select form in the template
    categories = request.dbsession.query(Category)
    return{'form': poll_form, 'categories': categories}


"""

@view_config(route_name='poll_in_full', renderer='../templates/view_poll_mobile.jinja2')
def poll_in_full(request):
    poll_id = request.matchdict.get('poll_id', -1)
    if poll_id != -1:
        return {'poll_id': poll_id}
    return {'er': 'say'}



@view_config(route_name='view_poll', renderer='json')
def view_poll(request):
    from ..services.feed_service import return_polls_voted_in
    dictt = {}
    #body = request.json_body
    poll_id = request.matchdict.get('poll_id', -1)
    if poll_id == -1:
        return {}
    poll = request.dbsession.query(Poll).filter(Poll.id==poll_id).first()
    poll_options = poll.options

    options_with_image = [option for option in poll.options if option.image_link is not None] 
    dictt['userLoggedIn'] = True if request.user else False
    dictt['type'] = 'poll'
    dictt['isPicturePoll'] =  True if options_with_image != [] else False
    dictt['id'] = str(poll.id)
    dictt['userName'] = poll.added_by.full_name
    dictt['userPic'] = poll.added_by.profile_picture
    dictt['question'] = poll.question
    dictt['info'] = poll.info
    dictt['imageInfo'] = poll.info_image_link
    dictt['timeAdded'] = poll.time_added
    dictt['timeRemaining'] = poll.time_remaining
    dictt['totalVotes'] = poll.num_of_votes
    

    dictt['options'] = []
    for option in poll_options:
        option_dictt = {'id': option.id, 
                        'option': option.title,
                        'score': option.num_of_votes}
        dictt['options'].append(option_dictt)

    #return {'poll': poll}

    #if user is logged in, find out whether he has voted
    if request.user: 
        user = request.dbsession.query(User).filter(User.id==request.user.id).first()
        polls_voted_in = return_polls_voted_in(request, user)
        dictt['userHasVoted']= poll.id in polls_voted_in or poll.poser == request.user.id
        
        dictt['hasEnded'] = False

    else:
        dictt['userHasVoted']= False
        dictt['hasEnded'] = False
    return dictt

    for comment in poll.comments: 
        comments = {'id': comment.id, 
                    'commenter_id': comment.commenter_id,
                    'comment': comment.comment,
                    'option_id': comment.option_id,
                    'timeAdded': comment.time_added}
        dictt['comments'].append(comments)


@view_config(route_name='view_poll_results', renderer='json')
def view_results(request):
    body = request.json_body
    poll_id = body.get('poll_id')
    voter_id = request.user.id

    seen_result = SeenResults()
    seen_result.poll_id = poll_id
    seen_result.voter_id = voter_id

    try:
        request.dbsession.add(seen_result)
    except Exception:
        return {'error': 'error'}
    
    return {'success': 'success'}



@view_config(route_name='poll_metrics', renderer='../templates/show_poll_metrics.jinja2')
def poll_gender_distribution(request):
    poll_id = request.matchdict.get('poll_id', -1)
    #we need to get details abouthe poll like name and stuff
    poll = request.dbsession.query(Poll).filter(Poll.id==poll_id).first()
    return {'poll': poll}
    


@view_config(route_name='get_metrics', renderer='json')
def get_metrics(request):
    main_focus = request.params.get('m_f')
    sub_focus = request.params.get('s_f')
    main_focus_objects = request.params.get('m_f_objs')
    sub_focus_objects = request.params.get('s_f_objs')
    poll_id = request.matchdict.get('poll_id')

    #we can't pass a list through the params, so let's get the sub
    # the sub_focus_object when it is options
    if sub_focus_objects == 'options':
        poll = request.dbsession.query(Poll).filter(Poll.id==poll_id).first()
        sub_focus_objects = [option.id for option in poll.options]
    else:
        if main_focus == 'age_range':
            sub_focus_objects = sub_focus_objects
        else:
            sub_focus_objects = int(sub_focus_objects)
    
    if main_focus and sub_focus and main_focus_objects and sub_focus_objects and poll_id:
        request.response.status = '200'
    else:
        request.response.status = '400'

    new_metrics = MetricsAggregator(main_focus, main_focus_objects, sub_focus, sub_focus_objects, poll_id)
    
    store = None
    if main_focus == 'age' or main_focus == 'age_range':
        store = PollVotersAgeStorage
    elif main_focus == 'gender':
        store = PollVotersGenderStorage
        

    derived_metrics = new_metrics.get_metrics(store)

    return derived_metrics


@view_config(route_name='get_voters_on_poll', renderer='json')
def get_voters_on_poll(request):
    voters = []
    poll_id = request.matchdict.get('poll_id', None)
    start_index = request.matchdict.get('s', None)
    end_index = request.matchdict.get('e', None)
    

    if not start_index and end_index: 
        start_index = 0
        end_index = 30

    if poll_id: 
        user_votes = request.dbsession.query(PollVotes).filter(PollVotes.poll_id==poll_id)[start_index:end_index]
    
    for vote in user_votes: 
        user_dict = {}
        user_dict['userFullName'] = vote.added_by.full_name
        user_dict['userPic'] = vote.added_by.profile_picture
        voters.append(user_dict)
    return voters


@view_config(route_name='all_polls', renderer='json')
def all_polls(request):
    polls = request.dbsession.query(Poll)
    dictt =  {'polls': []}
    for poll in polls:
        dictt['polls'].append(poll.question)

    return dictt


@view_config(route_name='polls_voted_in_page', renderer='../templates/polls_voted_in_page.jinja2')
def polls_voted_in_page(request):
    user = request.dbsession.query(User).filter(User.id==request.user.id).first()

    return {'user': user}

@view_config(route_name='get_polls_voted_in', renderer='json')
def get_polls_voted_in(request):
    user = request.dbsession.query(User).filter(User.id==request.user.id).first()
    dictt = {'activities': []}
    polls_voted_in = user.polls_voted_in
    polls_voted_in = [poll.poll_id for poll in polls_voted_in]

    polls = request.dbsession.query(Poll).filter(Poll.id.in_(polls_voted_in)).all()

    for poll in polls:
        poll_dictt = compile_poll_details(request, poll, user)
        dictt['activities'].append(poll_dictt)

    return dictt