from django.conf.urls import url

from rest_framework import routers

from users.views import UserViewSet, SwitchRoleView
from users.views import CustomizedTokenObtainPairView, CustomisedTokenRefreshView
from users.views import CustomisedTokenVerifyView
from users.views import RequestView, RegistrationView, ResetPasswordView
from users.views import SystemEmailView
from users.views import UserCreationView


router = routers.DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = router.urls

urlpatterns += [
    url(r'^login/$',                   CustomizedTokenObtainPairView.as_view(), name='token_obtain_pair'         ),
    url(r'^login/refresh/$',           CustomisedTokenRefreshView.as_view(),    name='token_refresh'             ),
    url(r'^login/switch_role/$',       SwitchRoleView.as_view(),                name='switch_role'               ),
    url(r'^login/verify/$',            CustomisedTokenVerifyView.as_view(),     name='token_verify'              ),

    url(r'^request/$',                 RequestView.as_view(),                   name='request'                   ),
    url(r'^register/$',                RegistrationView.as_view(),              name='registration'              ),
    url(r'^reset_password/$',          ResetPasswordView.as_view(),             name='password_reset'            ),

    url(r'^create_user/$',             UserCreationView.as_view(),              name='user_creation_with_details'),

    url(r'^system_generated_email/$',  SystemEmailView.as_view(),               name='system_email'              ),
]