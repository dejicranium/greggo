def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    
    config.add_route('register', '/register')
    config.add_route('xhr_register', '/xhr_register')


    #login routes
    config.add_route('login', '/login')
    config.add_route('xhr_login', '/xhr_login')     #for ajax
    config.add_route('verify_first_register_stage', '/verify_first_register')

    config.add_route('logout', '/logout')

    config.add_route('create_question', '/ask')

    config.add_route('vote', '/vote/')
    config.add_route('show_users', '/users')
    config.add_route('view_user', '/user/{id:\d+}/{slug}')

    config.add_route('view_poll', '/poll/{poll_id:\d+}')
    config.add_route('view_opinion', '/opinion/{opinion_id:\d+}')
    config.add_route('view_opinion_page', '/opinion/{opinion_id:\d+}/')
    config.add_route('get_opinion_metrics', '/opinion/{opinion_id:\d+}/metrics')

    config.add_route('add_categories', '/categories')

    
    config.add_route('view_profile', '/profile/{user_id:\d+}/')
    config.add_route('edit_profile', '/edit/profile/{user_id:\d+}')
    config.add_route('get_slug', '/slug/{user_id:\d+}')
    
    config.add_route('category', '/category/{category_id:\d+}')


    #comments
    config.add_route('add_comment', '/comment/')
    config.add_route('view_comments', '/comments/{poll_id:\d+}')
    config.add_route('view_opinion_comments', '/comments/opinion/{opinion_id:\d+}')
    config.add_route('view_option_comments', '/comments/option/{option_id:\d+}')
    config.add_route('agree_with_comments', '/agree')
    
    #testing purposes
    config.add_route('get_num_of_votes', '/getvotesfor/{poll_id:\d+}')
    config.add_route('show_categories', '/show/categories')
    config.add_route('subscribe_to_category', '/subscribe/category/{category_id:\d+}')
    config.add_route('show_subscriptions', '/show_subscriptions')
    config.add_route('show_subscribers', '/subscribers/{category_id:\d+}')

    config.add_route('follow_user', '/follow/{user_id:\d+}')
    config.add_route('unfollow_user', '/unfollow/{user_id:\d+}')
    config.add_route('followers', '/followers')
    config.add_route('followings', '/followings')

    config.add_route('see_polls', '/mypolls')
    config.add_route('test_mobile', '/test/mobile')
    config.add_route('get_latest_posts', '/get/latest')
    config.add_route('mobile_feed', '/mobile/feed')
    config.add_route('activities', '/activities')

    #test feed
    config.add_route('poll_in_full', '/poll/{poll_id:\d+}/')
    config.add_route('poll_metrics', '/poll/demographic-metrics/{poll_id:\d+}')
    config.add_route('opinion_metrics', '/opinion/demographic-metrics/{opinion_id:\d+}')

    config.add_route('get_metrics', '/get-metrics/{poll_id:\d+}')
    config.add_route('view_poll_results', '/viewresults')
    config.add_route('show_results', '/show_results')

    config.add_route('like', '/like/')
    config.add_route('unlike', '/unlike/')
    config.add_route('create_opinion', '/new/opinion')
    config.add_route('add_cat', '/add/categories')
    config.add_route('share', '/share/')

    config.add_route('get_voters_on_poll', '/voters/{poll_id:\d+}')
    config.add_route('get_user_polls', '/polls/user_id={user_id:\d+}')
    config.add_route('get_comment_and_replies', '/comments_and_replies/user_id={user_id:\d+}')
    config.add_route('get_likes_and_shares', '/likes_and_shares/user_id={user_id:\d+}')
    config.add_route('get_posts', '/posts/user_id={user_id:\d+}')
    
    config.add_route('delete_reply', '/delete-reply')
    config.add_route('reply_to_comment', '/reply-comment')
    config.add_route('reply_to_opinion', '/reply-opinion')
    config.add_route('reply_to_reply', '/reply-reply')
    config.add_route('all_polls', '/all/polls/')

    
    #notifications
    config.add_route('get_notifications', '/notifs/{user_id:\d+}')
    config.add_route('get_polls_from_category', "/get/polls/category_id={category_id:\d+}")
    config.add_route('category_polls_page', '/polls/category_id={category_id:\d+}')
    
    #config.add_route('agree_with_opinion', )
    config.add_route('trending_page', '/trending')
    config.add_route('get_trending', '/get_trending')

    config.add_route('view_conversation_page', '/view_conversation/conversation_id={conversation_id:\d+}/reply_id={reply_id:\d+}')
    config.add_route('get_conversation', '/get_conversation/{conversation_id:\d+}/{reply_id:\d+}')



    config.add_route('view_comment_page', '/view_comment/{comment_id:\d+}')
    config.add_route('get_comment', '/get_comment/{comment_id:\d+}')


    config.add_route('polls_voted_in_page', '/polls_voted_in/')
    config.add_route('get_polls_voted_in', '/get_polls_voted_in')

    config.add_route('get_comment_replies', '/replies/comment_id={comment_id:\d+}')
    config.add_route('get_reply_replies', '/replies/reply_id={reply_id:\d+}')

    config.add_route('view_reply_page', '/view_reply/{reply:\d+}')

    config.add_route('get_locations', '/get-locations')