from django.conf.urls import url

from rest_framework import routers
from jobs.views import JobViewSet,TaskViewSet,TaskView
from jobs.views import JobView
from jobs.views import WorkersEngagedView
from jobs.views import QATView

router = routers.DefaultRouter()
router.register(r'jobs', JobViewSet, base_name='jobs')
router.register(r'tasks', TaskViewSet, base_name='tasks')
urlpatterns = router.urls


urlpatterns += [

    url(r'task$'              , TaskView.as_view()              , name="get_task"),
    url(r'workers_engaged$'   , WorkersEngagedView.as_view()    , name="get_workers_worked_on_job"),
    url(r'results$'           , JobView.as_view()               , name="get_results"),
    url(r'qats$'              , QATView.as_view()               , name="get_qats"),
]

