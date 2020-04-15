from django.conf.urls import url, include
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view


#
# Schema View for Swagger documentation
#
#https://django-rest-swagger.readthedocs.io/en/latest/
#
schema_view = get_swagger_view(title='W3villa API')

urlpatterns = [
    url(r'^docs/', include_docs_urls(title='W3villa API', description='RESTful API for W3villa')),
    url(r'^swagger/', schema_view),

    url(r'^', include(('jobs.urls', 'jobs'), namespace='jobs')),
    url(r'^', include(('users.urls', 'users'), namespace='users')),
    
]
