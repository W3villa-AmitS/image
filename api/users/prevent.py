#
# Considered solution to prevent brute force attack as specified below:
#   https://stackoverflow.com/questions/49936101/how-to-prevent-brute-force-attack-in-django-rest-using-django-rest-throttling
#
from rest_framework.throttling import SimpleRateThrottle
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password


class UserLoginRateThrottle(SimpleRateThrottle):
    scope = 'failed_login_attempts'

    def get_cache_key(self, request, view):
        user  = get_user_model().objects.filter(username=request.data.get('username'))
        ident = user[0].pk if user else self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None:
            return True

        key = self.get_cache_key(request, view)
        if key is None:
            return True

        self.history = self.cache.get(key, [])
        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()

        if len(self.history) >= self.num_requests:
            return self.throttle_failure()

        return self.throttle_success(request)

    def throttle_success(self, request):
        """
        Inserts the current request's timestamp along with the key
        into the cache.
        """
        user = get_user_model().objects.filter(username=request.data.get('username'))
        if not user or user and not check_password(request.data.get('password').strip(), user[0].password):
            self.history.insert(0, self.now)

        # get a fresh key instead
        key = self.get_cache_key(request, None)
        if key is None:
            return True

        self.cache.set(key, self.history, self.duration)
        return True
