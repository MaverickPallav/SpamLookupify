from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, NotAuthenticated):
        request = context.get('request')
        session_id = request.COOKIES.get('sessionid')
        csrf_token = request.COOKIES.get('csrftoken')

        if not session_id and not csrf_token:
            response.data = {
                "detail": "Please register an account"   
            }
        elif csrf_token:
            response.data = {
                "detail": "You are not logged in. Please login."
            }

    return response