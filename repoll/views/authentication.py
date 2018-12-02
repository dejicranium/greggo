from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import transaction
from sqlalchemy.exc import DBAPIError
from webhelpers2.text import urlify



from ..services.auth_service import upload_profile_picture

import os
import uuid
import shutil
from ..form import PollCreateForm, LoginForm
from ..models.main_models import *
from ..form import RegistrationForm
from pyramid.security import remember, forget

from greggo.storage.redis.category_subscription import *


def register_user_to_redis(id, details):
    storage = UserInfoStorage()
    storage.create_user(id, details)

@view_config(route_name="xhr_login", renderer='json')
def login_through_xhr(request):
    next_url = request.referrer
    xhr_login_email = request.params.get('email')
    xhr_login_password = request.params.get('password')
    
    if xhr_login_email and xhr_login_password: 
        from pyramid.response import Response
        user = request.dbsession.query(User).filter_by(email=xhr_login_email).first()
        if user and user.verify_password(xhr_login_password):
            headers = remember(request, user.id)
            response = Response
            return HTTPFound(location=next_url, headers=headers)
        else:
            request.response.status = '400'
            return {'error': 'Username or password is incorrect'}
        
        request.response.status = '400'
        return {'could not verify': True} 


@view_config(route_name='verify_first_register_stage', renderer='json')
def verify_first(request):
    stage = request.json_body.get('stage', None)

    if stage:
        if stage == '1':
            email = request.json_body.get('email')
            username = request.json_body.get('username')
            phone = request.json_body.get('phone')

            email = request.dbsession.query(User).filter_by(email=email)
            if email.scalar() is not None:
                request.response.status = "400"
                return {'error': 'Email already exists'}
            
            username = request.dbsession.query(User).filter_by(username=username)
            if username.scalar() is not None:
                request.response.status = "400"
                return {'error': 'Username already exists'}


            phone = request.dbsession.query(User).filter_by(phone_number=phone)
            if phone.scalar() is not None:
                request.response.status = "400"
                return {'error': "Phone number already exists"}
        
        request.response.status = '200'
        return {}

@view_config(route_name='xhr_register', renderer='json')
def register_through_xhr(request):
    req_body = request.params
    first_name = req_body.get('firstName')
    last_name = req_body.get('lastName')
    username = req_body.get('username')
    password = request.params.get('password')
    email = req_body.get('email')
    phone = req_body.get('phone')
    sex = req_body.get('sex')
    birth_date = req_body.get('birthDate')
    birth_month = req_body.get('birthMonth')
    birth_year = req_body.get('birthYear')
    country = req_body.get('country')
    sub_unit = req_body.get('subUnit')

    profile_pic = req_body.get('profilePic', None)
    categories = req_body.get('categories', None)

        
    categories_list = categories.split(',')
    category_subs = []
    
    try:
        new_user = User()
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.email = email
     
        new_user.set_password(password)
        new_user.username = username
        new_user.phone_number = str(phone)
        new_user.sex = sex
        new_user.birth_date = int(birth_date)
        new_user.birth_month = birth_month
        new_user.birth_year = int(birth_year)
        new_user.country = int(country)
        new_user.sub_unit = int(sub_unit)

        if profile_pic != None:
            try:
                if profile_pic.file != None:
                    pic_file = profile_pic.file
                    pic_name = "{}".format(uuid.uuid4())
                    uploaded_pic = upload_profile_picture(pic_file, pic_name)
                    new_user.profile_picture = uploaded_pic['secure_url']
            except:
                print('we')
        

        request.dbsession.add(new_user)
        request.dbsession.flush()
        new_user.slug =  urlify(new_user.full_name)
        
        for category in categories_list: 
            new_sub = CategorySubscriber()
            new_sub.category_id = int(category)
            new_sub.user_id = new_user.id

            new_user.subscriptions.append(new_sub)
                #redis
            redis_category_subscription = CategorySubscription(int(category))
            redis_category_subscription.add_subscriber(new_user.id)

            
        transaction.commit()



    except Exception as e:
        request.response.status = '400' 
        return {'status': e}
    else: 
        request.response.status = '200'
        return {'success': 'success'}
    
    


"""
#this is the function that is called when twe go to the url to register
@view_config(route_name='register', renderer='../templates/register.jinja2')
def register_through_url(request):
    user_form = RegistrationForm(request.POST)
    age = request.POST.get('age', -1)
    location = request.params.get('location', -1)
    uploaded_pic = None

    user_details_dict = {}
    
    if request.method =="POST":
        picture = request.POST.get('profile-picture', -1)
        if picture != -1: 
            try:
                profile_picture = picture.file
        

        #give unique file name to picture
                pic_name = "{}.jpg".format(uuid.uuid4())
        
        #upload profile picture
                uploaded_pic = upload_profile_picture(profile_picture, pic_name)
            except Exception as e:
                print("couldn't")



        new_user = User(first_name=user_form.first_name.data,
                        last_name=user_form.last_name.data,
                        email=user_form.email.data)
        new_user.set_password(user_form.password.data)
        if uploaded_pic:
            new_user.profile_picture = uploaded_pic['secure_url']
        new_user.sex = request.POST.get('sex')



        

        if location != -1:
            new_user.location = location
        request.dbsession.add(new_user)
        request.dbsession.flush()



        user_details_dict['first_name'] = new_user.first_name
        user_details_dict['last_name'] = new_user.last_name
        user_details_dict['email'] = new_user.email
        user_details_dict['location'] = new_user.location
        user_details_dict['password'] = new_user.password


        register_user_to_redis(new_user.id, user_details_dict)

        return HTTPFound(location=request.route_url('home'))
    return {'form':user_form}

"""

def login_user(request, email, password, next_url=None):
    from pyramid.response import Response 
    if not next_url:
        next_url = request.referrer
    
    user = request.dbsession.query(User).filter_by(email=email).first()
    if user and user.verify_password(password):
        headers = remember(request, user.id)
        response = Response
        return HTTPFound(location=next_url, headers=headers)
    request.response.status = '400'
    return {'error': 'error'}



@view_config(route_name='login', renderer='../templates/login.jinja2')
def login(request):
    """    
    next_url = request.params.get('next', request.referrer)
    

    email = request.params.get('email', -1)
    password = request.params.get('password', -1)

    if email != -1 and password != -1:
        user = request.dbsession.query(User).filter_by(email=email).first()
        if user and user.verify_password(password):
            request.response.status = '200'
            headers = remember(request, user.id)
            return HTTPFound(location=next_url, headers=headers)
        request.response.status = '400'
        return {'error': 'error'}
    """

    """
    if request.json_body != '{}':
        body = request.json_body
        if body:
            xhr_login_email = body.get('xhr_login_email')
            xhr_login_password = body.get('xhr_login_password')
    
            if xhr_login_email and xhr_login_email: 
                from pyramid.response import Response
                user = request.dbsession.query(User).filter_by(email=xhr_login_email).first()
                if user and user.verify_password(xhr_login_password):
                    headers = remember(request, user.id)
                    response = Response
                    return HTTPFound(location=next_url, headers=headers)
                else:
                    return {'error': 'error'}
           
            return {'could not verify': True}
    

    """
    next_url = request.params.get('next', request.route_url('mobile_feed'))

    if not next_url or next_url == request.route_url('login'):
        next_url = request.route_url('mobile_feed')
    error = ''

    if 'form.submitted' in request.params:
        email = request.params['email']
        password = request.params['password']
        user = request.dbsession.query(User).filter_by(email=email).first()
        if user and user.verify_password(password):
            headers = remember(request, user.id)
            return HTTPFound(location=next_url, headers=headers)
        error = 'Email address or password is incorrect.'
        return {'error': error}
    
    if request.user:                                    #if user is already logged in
        return HTTPFound(location=next_url)

  

    
    return dict(                                        #else, request method is GET
        error = error,
        url = request.route_url('login'),
       )
    

    

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    next_url = request.route_url('login')
    return HTTPFound(location=next_url, headers=headers)
