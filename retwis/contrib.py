from models import User

class AuthenticationMiddleware(object):
    def process_request(self, request):
        auth_user = None
        if 'auth' in request.COOKIES:
            check_user_id = User.check_auth_secret(request.COOKIES['auth'])
            if check_user_id:
                auth_user = User.fetch_one(check_user_id)

        if auth_user:
            request.user = auth_user
        else:
            request.user = User(0, '')

        return None
