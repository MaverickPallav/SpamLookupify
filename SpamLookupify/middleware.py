from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog
import json

class CSRFCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):

        csrf_token = request.COOKIES.get('csrftoken')
        if csrf_token:
            request.META['HTTP_X_CSRFTOKEN'] = csrf_token

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user if request.user.is_authenticated else None

        if request.method == 'POST':
            try:
                data = request.POST.dict()
                if not data:
                    data = json.loads(request.body)
            except json.JSONDecodeError:
                data = {}
        else:
            data = request.GET.dict()

        RequestLog.objects.create(
            user=user,
            request_type=request.method,
            request_path=request.path,
            data=data
        )