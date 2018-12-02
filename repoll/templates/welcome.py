{% block content %}
    {% if request.authenticate_userid %}
    	<h1>You are welcome </h1>
    {% else %}
    	<h1>You are not logged in

{% endblock}
