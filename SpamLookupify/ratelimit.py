from rest_framework.throttling import UserRateThrottle

class RegisterThrottle(UserRateThrottle):
    rate = '10/hour'  

class LoginThrottle(UserRateThrottle):
    rate = '5/minute' 

class LogoutThrottle(UserRateThrottle):
    rate = '20/minute'

class ContactThrottle(UserRateThrottle):
    rate = '10/minute'

class ReportSpamThrottle(UserRateThrottle):
    rate = '10/minute'
    day_rate = '50/day'

class SearchThrottle(UserRateThrottle):
    rate = '1/minute'
    day_rate = '200/day'