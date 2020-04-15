from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class CustomisedRefreshToken(RefreshToken):
    """
    Customised to update the user roles and login related details
    on each refresh call.
    """
    @property
    def access_token(self):
        access_token = super(CustomisedRefreshToken, self).access_token

        user = User.objects.get(pk=int(access_token.payload['user_id']))

        for claim in ['roles', 'active_role']:
            access_token[claim] = getattr(user, claim)

        return access_token

