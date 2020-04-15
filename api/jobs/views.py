import re
from math import ceil
from collections import defaultdict

from rest_framework import viewsets
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, NotAcceptable

from rest_condition import And, Or

from users.permissions import IsAdmin, IsSearcher, IsManager, IsWorker
from users.permissions import user_is_worker, user_is_searcher, user_is_manager
from users.models import Worker, TaskCompleted, User, UserInformation

from . import serializers
from . models import Task, Job
from .tasks import extract_qats_and_wots

from . task_scheduler import TaskScheduler
from . task_scheduler import WorkerAlreadyActive, WorkerDisqualifiedOnJob, ModelError

from .service_calls import AnnotationAnalysisAndProcessingApi
from .service_calls import ResponseError, ConnectivityError, URLError

#
# helper functions
#
def qats_required(initial_qats, number_of_wots, qat_frequency):
    """
    Calculate the number of QATs required for the Job to qualify for the approval.
    :param initial_qats:  initial number of QATs to be added.
    :param number_of_wots: total number of WOTs added to Job.
    :param qat_frequency:  Number of WOTs after which intermittent QATs must be added.
    :return: total number of QATs requried for the job.
    """
    if qat_frequency > 0:
        return initial_qats + ceil(number_of_wots/qat_frequency) - 1
    return initial_qats

def request_from_user(request, user_id):
    """
    Check if the request is from the user specified by user_id.
    :param request:
    :param user_id:
    :return:
    """
    return int(request.user.id) == int(user_id)

class JobViewSet(viewsets.ViewSet):
    """
    create:
    Create a new Job.
    * Requires token authentication.
    * Only searcher users are able to access this view.

    list:
    Return a list of all existing jobs.
    * Requires token authentication.

    retrieve:
    Return the details of the given job.
    * Requires token authentication.

    job_approval:
    Alter the status of the job to 'approved' if it is either 'created' or 'disapproved'.
    * Requires token authentication.
    * Only manager users are able to access this view.

    job_disapproval:
    Alter the status of the job to 'disapproved' if it is either 'created' or 'approved'.
    * Requires token authentication.
    * Only manager users are able to access this view.

    add_tasks:
    Add tasks to a job in 'created' state.
    * Requires token authentication.
    * Only searcher users are able to access this view.
    """
    serializer_class = serializers.JobSerializer

    permission_classes_by_action = {
        #
        # inherited actions
        #
        'create'            : [And(IsAuthenticated, IsSearcher), ],                          # post
        'list'              : [And(IsAuthenticated, Or(IsSearcher, IsManager, IsWorker)), ], # get
        'retrieve'          : [And(IsAuthenticated, Or(IsSearcher, IsManager, IsWorker)), ], # get

        #
        # custom actions
        #
        'job_approval'      : [And(IsAuthenticated, IsManager), ],                          # post
        'job_disapproval'   : [And(IsAuthenticated, IsManager), ],                          # post
        'add_wots'          : [And(IsAuthenticated, IsSearcher), ],                         # post
        'add_qats'          : [And(IsAuthenticated, IsSearcher), ],                         # post
        'disengage'         : [And(IsAuthenticated, IsWorker), ],                           # post

        'consolidate'       : [And(IsAuthenticated, Or(IsSearcher, IsManager)), ],          # get

    }

    def create(self, request):
        serializer = serializers.JobSerializer(data=request.data)
        if serializer.is_valid():
            try:

                serializer.save( job_status = "initialized",
                                 job_owner  = request.user.id)

            except AssertionError as err:
                return Response({"error: {0}".format(err)}, status=status.HTTP_400_BAD_REQUEST)

            # filter the serializer data to return
            allowed_fields = ['job_id', 'job_name', 'job_type', 'job_max_occurrence', 'job_attributes']
            filtered_dict  = {key: val for (key, val) in serializer.data.items() if key in allowed_fields }

            # for picture boxing job type check if any specific boxing type is strictly expected
            if serializer.data.get('job_type') == 'P':
                boxing_type = serializer.data.get('job_boxing_type')
                if boxing_type:
                    filtered_dict['job_boxing_type'] = boxing_type

            return Response(filtered_dict, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):

        jobs = Job.fetch_all_jobs()
        print(jobs)

        #
        # filter on status if query string specified
        #
        if request.GET and 'status' in request.GET:
            filtered_jobs = []
            for stat in dict(request.GET)['status']:
                if stat in serializers.JobSerializer.status_choices:
                    filtered_jobs += [job for job in jobs if job['job_status'] == stat]
                else:
                    return Response({"error": "invalid status type '%s' specified."%stat}, status=status.HTTP_400_BAD_REQUEST)
            jobs = filtered_jobs

        serializer = serializers.JobSerializer(instance=jobs, many=True)

        if user_is_worker(request):
            eligible_jobs = []
            #
            # Todo: filter jobs on the basis of worker criteria
            #

            #
            # check if worker has already worked and completed all the tasks on this job
            #
            for job in serializer.data:
                if job['job_status'] in ("approved", "in_progress", "completed"):
                    try:
                        worker = Worker.objects.get(user_id=int(request.user.id), job_id=job['job_id'])
                        #
                        # fake the state of the job to distinguish the "completed by worker" jobs with "completed" jobs
                        #
                        if worker.is_completed:
                            job['job_status'] = "completed by worker"
                    except Worker.DoesNotExist:
                        pass

                    eligible_jobs.append(job)

            restricted_fields = ['job_initial_qats', 'job_qat_frequency']
            return Response([{k : v for k, v in elem.items() if k not in restricted_fields} for elem in eligible_jobs])

        elif user_is_searcher(request):
            return Response(filter(lambda job: int(job['job_owner']) == int(request.user.id), serializer.data))

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            job = Job.fetch_job(job_id=pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.JobSerializer(instance=job)

        if user_is_worker(request):
            #
            # Todo: filter jobs on the basis of worker criteria
            #
            job = serializer.data

            if job['job_status'] in ("approved", "in_progress", "completed"):

                #
                # check if worker has already worked and completed all the tasks on this job
                #
                try:
                    worker = Worker.objects.get(user_id=int(request.user.id), job_id=job['job_id'])
                    #
                    # fake the state of the job to distinguish the "completed by worker" jobs with "completed" jobs
                    #
                    if worker.is_completed:
                        job['job_status'] = "completed by worker"
                except Worker.DoesNotExist:
                    pass

                restricted_fields = ['job_initial_qats', 'job_qat_frequency']
                return Response({k:v for k,v in job.items() if not k in restricted_fields})
            return Response({})

        elif user_is_searcher(request) and not int(job['job_owner']) == int(request.user.id):
            return Response({})

        # prepare a return dict from serializer data
        return_dict = {key : val for key, val in serializer.data.items()}

        # calculate the required number of QATs
        total_qats_required = qats_required(job['job_initial_qats'],
                                            job['job_number_of_wots'],
                                            job['job_qat_frequency'])
        more_qats_required = 0
        if (total_qats_required - job['job_number_of_qats']) > 0:
            more_qats_required = total_qats_required - job['job_number_of_qats']

        # add the username of the job creator
        job_creator = User.objects.get(id=int(job['job_owner']))

        return_dict.update({
            "job_wots_status"                                : job['job_wot_status'],
            "job_qats_status"                                : job['job_qat_status'],
            "job_created_by"                                 : job_creator.username,
            "job_number_of_wots_added"                       : job['job_number_of_wots'] ,
            "job_number_of_qats_added"                       : job['job_number_of_qats'] ,
            "job_number_of_qats_to_appear_in_beginning"      : job['job_initial_qats']   ,
            "job_number_of_wots_after_which_a_qat_to_appear" : job['job_qat_frequency']  ,
            "job_number_of_total_qats_required"              : total_qats_required       ,
            "job_number_of_more_qats_required_to_add"        : more_qats_required        ,
        })
        return Response(return_dict)

    @action(methods=['post'], detail=True, url_path='approve', url_name='job_approval')
    def job_approval(self, request, pk=None, *args, **kwargs):
        try:
            job = Job.fetch_job(job_id=pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if job['job_status'] in ('finalized', 'disapproved'):

            # update the status of the job and schedule for the processing
            Job.update_status(job['job_id'], new_status="approving")

            try:
                extract_qats_and_wots.delay(job['job_id'])
            except AttributeError as err:
                return Response({"error": err.args[0]}, status=status.HTTP_403_FORBIDDEN)

            job = Job.fetch_job(job_id=pk)
            serializer = serializers.JobSerializer(instance=job)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response({"error": "Can't 'approve' a job in state of '%s'" % job['job_status']}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='disapprove', url_name='job_disapproval')
    def job_disapproval(self, request, pk=None, *args, **kwargs):
        try:
            job = Job.fetch_job(job_id=pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if job['job_status'] in ('finalized'):
            Job.update_status(job_id=pk, new_status='disapproved')
            job = Job.fetch_job(job_id=pk)
            serializer = serializers.JobSerializer(instance=job)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response({"error": "Can't 'disapprove' a job in state of '%s'" % job['job_status']}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='add_wots', url_name='task_addition')
    def add_wots(self, request, pk=None, *args, **kwargs):
        #
        # fetch the job in database
        #
        try:
            job = Job.fetch_job(job_id=pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        #
        # restrict the access to this view for only the user who created the corresponding job.
        #
        if not request.user.id == job['job_owner']:
            return Response({"error": "Only the author may post the tasks to a job."},
                            status=status.HTTP_401_UNAUTHORIZED)

        #
        # allow the addition of tasks only if the job is in state 'created'.
        #
        if job['job_status'] in ('initialized', 'being_created', 'wots_added'):
            serializer = serializers.AddWOTSerializer(data=request.data)

            if serializer.is_valid():
                try:
                    serializer.save(job_id=pk, max_occurrence=int(job['job_max_occurrence']))

                    # fetch the details of the updated job
                    job = Job.fetch_job(job_id=pk)

                    # prepare a return dict from serializer data
                    return_dict = {}

                    # calculate the required number of QATs
                    total_qats_required = qats_required(job['job_initial_qats'],
                                                        job['job_number_of_wots'],
                                                        job['job_qat_frequency'])
                    more_qats_required = 0
                    if (total_qats_required - job['job_number_of_qats']) > 0:
                        more_qats_required = total_qats_required - job['job_number_of_qats']

                    return_dict.update({
                        "success" : "WOTs scheduled to add successfully.",
                        "job_number_of_wots_scheduled_to_add": job['job_number_of_wots'],
                        "job_number_of_qats_added": job['job_number_of_qats'],
                        "job_number_of_qats_to_appear_in_beginning": job['job_initial_qats'],
                        "job_number_of_wots_after_which_a_qat_to_appear": job['job_qat_frequency'],
                        "job_number_of_total_qats_required": total_qats_required,
                        "job_number_of_more_qats_required_to_add": more_qats_required,
                    })

                    return Response(return_dict, status=status.HTTP_202_ACCEPTED)

                except AssertionError as err:
                    return Response({"error": "{0}".format(err)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Can't add tasks to a job in state '%s'" % job['job_status']},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='add_qats', url_name='qats_addition')
    def add_qats(self, request, pk=None, *args, **kwargs):
        #
        # fetch the job in database
        #
        try:
            job = Job.fetch_job(job_id=pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        #
        # restrict the access to this view for only the user who created the corresponding job.
        #
        if not request.user.id == job['job_owner']:
            return Response({"error": "Only the author may post the tasks to a job."},
                            status=status.HTTP_401_UNAUTHORIZED)

        #
        # allow the addition of QATs only if there already are added some WOTs.
        #
        if job['job_number_of_wots'] == 0:
            return Response({"error": "Can't add a QAT to a job with no WOTs"},
                            status=status.HTTP_400_BAD_REQUEST)

        #
        # allow the addition of tasks only if the job is in state 'created'.
        #
        if not job['job_status'] in ('being_created', 'wots_added'):
            return Response({"error": "Can't add tasks to a job in state '%s'" % job['job_status']},
                            status=status.HTTP_400_BAD_REQUEST)

        #
        # allow the addition of QATS only if there is a need of QATs.
        #

        # calculate the required number of QATs
        total_qats_required = qats_required(job['job_initial_qats'],
                                            job['job_number_of_wots'],
                                            job['job_qat_frequency'])

        more_qats_required = total_qats_required - job['job_number_of_qats']
        if more_qats_required <= 0:
            return Response({"error": "Can't add more QATs to Job. Already added the required number of QATs"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.AddQATSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save(job_id=pk)
            except AssertionError as err:
                return Response({"error": "{0}".format(err)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # fetch the details of the updated job
        job = Job.fetch_job(job_id=pk)

        # prepare a return dict from serializer data
        return_dict = {}

        # calculate the required number of QATs
        total_qats_required = qats_required(job['job_initial_qats'],
                                            job['job_number_of_wots'],
                                            job['job_qat_frequency'])

        more_qats_required = total_qats_required - job['job_number_of_qats']
        if job['job_status'] == 'wots_added' and more_qats_required <= 0:
            Job.update_status(job_id=pk, new_status="finalized")

        return_dict.update({
            "success": "QAT added successfully",
            "job_number_of_wots_added": job['job_number_of_wots'],
            "job_number_of_qats_added": job['job_number_of_qats'],
            "job_number_of_qats_to_appear_in_beginning": job['job_initial_qats'],
            "job_number_of_wots_after_which_a_qat_to_appear": job['job_qat_frequency'],
            "job_number_of_total_qats_required": total_qats_required,
            "job_number_of_more_qats_required_to_add": more_qats_required,
        })
        return Response(return_dict, status=status.HTTP_202_ACCEPTED)


    @action(methods=['post'], detail=True, url_path='disengage', url_name='disengage_worker')
    def disengage(self, request, pk=None, *args, **kwargs):
        try:
            worker_allocation = list(Worker.objects.filter(job_id=pk, user_id=int(request.user.id)))
        except ValueError:
            return Response({"error": "Specified an invalid job_id."}, status=status.HTTP_400_BAD_REQUEST)

        if worker_allocation:
            if len(worker_allocation) > 1 :
                return Response({"error": "Multiple entries for the user activation on the specified job."}, status=status.HTTP_400_BAD_REQUEST)
                # ideally this case must never happen

            if worker_allocation[0].is_active:
                worker_allocation[0].is_active = False
                worker_allocation[0].save()
                return Response(status=status.HTTP_202_ACCEPTED)

            return Response({"error": "Worker is not active on this job."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Unable to find worker allocation on job with specified job_id."}, status=status.HTTP_404_NOT_FOUND)

    # custom action to get the consolidated view of the task results
    @action(methods=['get'], detail=True, url_path='consolidate', url_name='consolidated_result_for_job',)
    def consolidate(self, request, pk=None, *args, **kwargs):
        #
        # fetch the job in database
        #
        try:
            job = Job.fetch_job(job_id=pk)
        except KeyError:
            return Response({"error": "Invalid job_id."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid job_id."}, status=status.HTTP_400_BAD_REQUEST)

        #
        # check if job is completed
        #
        if job['job_status'] != "completed":
            return Response({"error": "Job is not completed yet."}, status=status.HTTP_403_FORBIDDEN)

        # allow access only to a manager or a searcher if owner of this job
        if user_is_manager(request) or \
                (user_is_searcher(request) and request_from_user(request, job['job_owner'])):

            results = {}

            for task in job['job_wots']:
                task = Task.fetch_task(task)

                result = {}

                # form the json to send the required information
                input = dict()

                input['results']     = task['results']
                input['job_type']    = job['job_type']
                input['boxing_type'] = job['job_boxing_type']

                try:
                    consolidated_annotations = AnnotationAnalysisAndProcessingApi.consolidate(input)
                except ResponseError as err:
                    return Response(err.args[0], status=status.HTTP_400_BAD_REQUEST)
                except ConnectivityError:
                    return Response({"error": "Microservice Error: Problems in connectivity."}, status=status.HTTP_400_BAD_REQUEST)
                except URLError:
                    return Response({"error": "Microservice Error: Invalid URL requested."}, status=status.HTTP_400_BAD_REQUEST)

                # form the json to return
                result['image_url'] = task['image_url']
                result['result']    = consolidated_annotations

                results[str(task['task_id'])] = result

            return Response(results, status=status.HTTP_200_OK)

        return Response({"error": "User is not authorized for this call."}, status=status.HTTP_401_UNAUTHORIZED)

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    #
    # unsupported actions
    #
    def partial_update(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)


class TaskView(APIView):
    """
    View to get a task.

    * Requires token authentication.
    * Only worker users are able to access this view.
    """
    permission_classes = (IsAuthenticated, IsWorker, )

    def get(self, request):
        job_id = request.GET.get('job_id', None)

        match = re.match(r'(?P<job_id>^[a-zA-Z0-9]{8})', job_id)
        if match:
            job_id = match.group('job_id')

        if not job_id:
            return Response({"error": "job_id is not provided"}, status=status.HTTP_400_BAD_REQUEST)


        #
        # Case 1: Job is already completed
        #
        job = Job.fetch_job(job_id=job_id)
        if job['job_status'] in ('completed', 'validated', 'rejected'):
            return Response({"error": "Job is already completed."}, status=status.HTTP_204_NO_CONTENT)


        #
        # Case 2: Job is not approved yet
        #
        if not job['job_status'] in ('approved', 'in_progress'):
            return Response({"error": "Job is not yet approved."}, status=status.HTTP_403_FORBIDDEN)

        #
        # Case 3: Job is not completed yet
        #
        # restrict the exposure to a limited  set of task attributes
        attributes_to_expose = ['task_id', 'image_url']
        try:
            next_task = TaskScheduler.get_next_task(job_id=job_id, user_id=int(request.user.id))
        except WorkerAlreadyActive as obj:
            return Response({"error": obj.args[0], 'job_id': obj.args[1]}, status=status.HTTP_400_BAD_REQUEST)
        except (WorkerDisqualifiedOnJob, ModelError) as obj:
            return Response({"error": obj.args[0]}, status=status.HTTP_400_BAD_REQUEST)

        # get the worker details
        user_activation = Worker.objects.get(job_id=job_id, user_id=int(request.user.id))

        if next_task:
            filtered_dict = {key: val for (key, val) in next_task.items() if key in attributes_to_expose}

            # add job specific details
            for field in ['job_id', 'job_name', 'job_type', 'job_description', 'job_instructions', \
                          'job_attributes', 'job_boxing_type']:
                filtered_dict[field] = job.get(field)

            # for picture boxing job type check if any specific boxing type is strictly expected
            # if job.get('job_type') == 'P':
            #     boxing_type = job.get('job_boxing_type')
            #     if boxing_type:
            #         filtered_dict['job_boxing_type'] = boxing_type


            # get task statistics
            task_stats = {
                            'tasks_completed': '%d' % len(user_activation.tasks_completed),
                            'total_tasks'    : '%s' % len(job['job_wots'] + job['job_qats'])
                          }

            return Response(dict(filtered_dict, **task_stats), status=status.HTTP_200_OK)
        else:
            user_activation.is_active    = False
            user_activation.is_completed = True
            user_activation.save()

            return Response({"error": "No more tasks left for the user on job with job_id '%s'" % (job_id)}, status=status.HTTP_204_NO_CONTENT)


class TaskViewSet(viewsets.ViewSet):
    """
    list: todo

    retrieve: todo

    post_result:
    Post the result of a task.
    * Requires token authentication.
    * Only worker users are able to access this view.
    """
    permission_classes_by_action = {
        #
        # inherited actions
        #
        'retrieve'    : [And(IsAuthenticated, Or(IsSearcher, IsManager, IsWorker)), ],  # get
        'list'        : [And(IsAuthenticated, Or(IsSearcher, IsManager, IsWorker)), ],  # get
        'post_result' : [IsAuthenticated, IsWorker                                  ],  # post
        'consolidate' : [And(IsAuthenticated, Or(IsSearcher, IsManager)),           ]   # get
    }

    # custom action created for updation of result as per task(result data of image annotation)
    @action(methods=['post'], detail=True, url_path='post_result', url_name='result_update',)
    def post_result(self, request, pk=None, *args, **kwargs):
        #
        # fetch the task requested for the update
        #
        try:
            task = Task.fetch_task(task_id=pk)
        except KeyError:
            return Response({'error': 'Invalid task'}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.AddResultSerializer(data=request.data, instance=task)

        if serializer.is_valid():
            try:
                result = serializer.update(task, serializer.validated_data, user_id=request.user.id)
            except (NotAcceptable, AssertionError) as err:
                return Response({'error': err.args[0]}, status=status.HTTP_406_NOT_ACCEPTABLE)
            except NotFound as err:
                return Response({'error': err.args[0]}, status=status.HTTP_404_NOT_FOUND)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            task = Task.fetch_task(task_id=pk)
        except KeyError:
            return Response({'error': 'Invalid task'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        #
        # fetch corresponding job details
        #
        try:
            job = Job.fetch_job(job_id=task['job_id'])
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user_is_manager(request):
            return Response(task)

        elif user_is_searcher(request):
            if not request_from_user(request, job['job_owner']):
                return Response({"error": "Requestor is not the owner of this task."}, status=status.HTTP_404_NOT_FOUND)
            return Response(task)

        elif user_is_worker(request):
            if not str(request.user.id) in task['results'].keys():
                return Response({"error": "No accepted submission from the worker on this task"}, status=status.HTTP_404_NOT_FOUND)

            return_dict = dict()
            return_dict['task_id']   = task['task_id']
            return_dict['image_url'] = task['image_url']
            return_dict['result']    = task['results'][str(task[request.user.id])]
            return Response(return_dict)

        return Response({"error": "User is not authorized for this call."}, status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request):
        #
        # filter on job_id if query string specified
        #
        if request.GET and 'job_id' in request.GET:
            # filter parameters
            jobs = []
            task_types = []

            for key, vals in dict(request.GET).items():
                # TODO Improve readability :Saurabh
                filtered_task_type_vals = [re.match(r'(qat|wot)', elem).group(1) for elem in vals if
                                           re.match(r'(qat|wot)', elem)]
                filtered_job_task_vals = [re.match(r'(^[a-zA-Z0-9]{8}$)', elem).group(1) for elem in vals if
                                          re.match(r'(^[a-zA-Z0-9]{8}$)', elem)]

                if key == 'job_id':
                    jobs.extend(filtered_job_task_vals)
                elif key == 'task_type':
                    task_types.extend(filtered_task_type_vals)

            if not jobs:
                return Response({"error": "Invalid or no job_id's specified."}, status=status.HTTP_400_BAD_REQUEST)

            for task_type in task_types:
                if task_type not in ('qat', 'wot'):
                    return Response({"error": "Invalid task_type '%s' specified."}, status=status.HTTP_400_BAD_REQUEST)

            if user_is_searcher(request) or user_is_manager(request):
                results = {}
                for job_id in jobs:
                    try:
                        job = Job.fetch_job(job_id=job_id)
                    except KeyError:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                    except ValueError:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                    #import pdb;pdb.set_trace()

                    if user_is_manager(request) or \
                            (user_is_searcher(request) and request_from_user(request, job['job_owner'])):
                        tasks = []
                        for task_id in job['job_wots'] + job['job_qats']:
                            task = Task.fetch_task(task_id=task_id)
                            #import pdb;pdb.set_trace()
                            this_task_type = 'qat' if task['is_qat'] else 'wot'
                            if (task_types and this_task_type in task_types) or (not task_types):
                                task['job_type']  = job['job_type']
                                tasks.append(task)
                        results[str(job_id)] = tasks

                return Response(results)

            if user_is_worker(request):
                worker_results = defaultdict(list)

                for job_id in jobs:
                    try:
                        job = Job.fetch_job(job_id=job_id)
                    except KeyError:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                    except ValueError:
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                    for task_id in job['job_wots'] + job['job_qats']:
                        task = Task.fetch_task(task_id=task_id)
                        if str(request.user.id) in task['results'].keys():
                            task_dict = dict()
                            task_dict['task_id']   = task['task_id']
                            task_dict['image_url'] = task['image_url']
                            task_dict['result']    = task['results'][str(request.user.id)]

                            # add the type of job
                            task_dict['job_type']  = job['job_type']

                            worker_results[str(job_id)].append(task_dict)

                return Response(worker_results)

            return Response({"error": "User is not authorized for this call."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"error": "Missing search parameter 'job_id' in the call."}, status=status.HTTP_400_BAD_REQUEST)

    #
    # unsupported actions
    #
    def create(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({'error': 'method not supported'}, status=status.HTTP_400_BAD_REQUEST)

    # custom action to get the consolidated view of the task results
    @action(methods=['get'], detail=True, url_path='consolidate', url_name='consolidated_result',)
    def consolidate(self, request, pk=None, *args, **kwargs):
        #
        # fetch the task requested for the update
        #
        try:
            task = Task.fetch_task(task_id=pk)
        except KeyError:
            return Response({'error': 'Invalid task'}, status=status.HTTP_404_NOT_FOUND)

        #
        # consolidation is applicable to only WOTs
        #
        if task['is_qat']:
            return Response({'error': 'Consolidation is not supported for Quality Assurance Tasks.'}, status=status.HTTP_403_FORBIDDEN)


        #
        # fetch the job in database
        #
        try:
            job = Job.fetch_job(job_id=task['job_id'])
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        #
        # check if task is completed
        #
        if not Task.completed(task):
            return Response({"error": "Task is not completed yet."}, status=status.HTTP_403_FORBIDDEN)


        # allow access only to a manager or a searcher if owner of this job
        if user_is_manager(request) or \
                (user_is_searcher(request) and request_from_user(request, job['job_owner'])):

            # form the json to send the required infomation
            input = dict()

            input['results']     = task['results']
            input['job_type']    = job['job_type']
            input['boxing_type'] = job['job_boxing_type']

            try:
                consolidated_annotations = AnnotationAnalysisAndProcessingApi.consolidate(input)
            except ResponseError as err:
                return Response(err.args[0], status=status.HTTP_400_BAD_REQUEST)
            except ConnectivityError:
                return Response({"error": "Microservice Error: Problems in connectivity."}, status=status.HTTP_400_BAD_REQUEST)
            except URLError:
                return Response({"error": "Microservice Error: Invalid URL requested."}, status=status.HTTP_400_BAD_REQUEST)

            # form the json to return
            result = {'image_url': task['image_url']}
            result['result'] = consolidated_annotations

            return Response(result, status=status.HTTP_200_OK)

        return Response({"error": "User is not authorized for this call."}, status=status.HTTP_401_UNAUTHORIZED)


    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]


class JobView(APIView):
    """
    View to get the annotations performed by user on different tasks of the job.

    * Requires token authentication.
    * Only manager and the owner of the job may access this view.
    """
    permission_classes = (And(IsAuthenticated, Or(IsManager, IsSearcher)), )

    def get(self, request):
        if request.GET and 'job_id' in request.GET:
            if user_is_searcher(request) or user_is_manager(request):
                results = {}

                # filter parameters
                jobs       = []
                workers    = []
                tasks      = []
                task_types = []

                for key, vals in dict(request.GET).items():
                    # TODO Improve readability :Saurabh
                    filtered_task_type_vals = [re.match(r'(qat|wot)', elem).group(1) for elem in vals if re.match(r'(qat|wot)', elem)]
                    filtered_vals = [re.match(r'(\d+)', elem).group(1) for elem in vals if re.match(r'(\d+)', elem)]
                    filtered_job_task_vals = [re.match(r'(^[a-zA-Z0-9]{8}$)', elem).group(1) for elem in vals if re.match(r'(^[a-zA-Z0-9]{8}$)', elem)]

                    if key == 'job_id':
                        jobs.extend(filtered_job_task_vals)
                    elif key == 'worker_id':
                        workers.extend(filtered_vals)
                    elif key == 'task_id':
                        tasks.extend(filtered_job_task_vals)
                    elif key == 'task_type':
                        task_types.extend(filtered_task_type_vals)

                if not jobs:
                    return Response({"error": "Invalid or no job_id's specified."}, status=status.HTTP_400_BAD_REQUEST)

                if tasks and task_types:
                    return Response({"error": "Filters 'task_id' and 'task_type' cannot be used together."}, status=status.HTTP_400_BAD_REQUEST)

                for task_type in task_types:
                    if task_type not in ('qat', 'wot'):
                        return Response({"error": "Invalid task_type '%s' specified."}, status=status.HTTP_400_BAD_REQUEST)

                for job_id in jobs:
                    try:
                        job = Job.fetch_job(job_id=job_id)
                    except KeyError:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                    except ValueError:
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                    if not job['job_status'] in ('in_progress', 'completed'):
                        return Response({"error": "Result from a job in state '%s' can't be fetched."% job['job_status']},
                                        status=status.HTTP_400_BAD_REQUEST)

                    if user_is_manager(request) or \
                            (user_is_searcher(request) and request_from_user(request, job['job_owner'])):

                        worker_task_map = defaultdict(lambda: dict())

                        for task_id in job['job_wots'] + job['job_qats']:
                            task = Task.fetch_task(task_id=task_id)

                            if tasks:
                                if str(task['task_id']) in tasks:
                                    for worker, work in task['results'].items():
                                        result = dict()
                                        result['is_qat']    = task['is_qat']
                                        result['image_url'] = task['image_url']

                                        result['worker'] = work

                                        if task['is_qat']:
                                            result['searcher'] = task['result']

                                        this_task_type = 'qat' if task['is_qat'] else 'wot'

                                        if workers:
                                            if worker in workers:
                                                if (task_types and this_task_type in task_types) or (not task_types):
                                                    worker_task_map[worker][str(task['task_id'])] = result
                                        else:
                                            if (task_types and this_task_type in task_types) or (not task_types):
                                                worker_task_map[worker][str(task['task_id'])] = result

                            else:
                                for worker, work in task['results'].items():
                                    result = dict()
                                    result['is_qat'] = task['is_qat']
                                    result['image_url'] = task['image_url']

                                    result['worker'] = work

                                    if task['is_qat']:
                                        result['searcher'] = task['result']

                                    this_task_type = 'qat' if task['is_qat'] else 'wot'

                                    if workers:
                                        if worker in workers:
                                            if (task_types and this_task_type in task_types) or (not task_types):
                                                    worker_task_map[worker][str(task['task_id'])] = result
                                    else:
                                        if (task_types and this_task_type in task_types) or (not task_types):
                                            worker_task_map[worker][str(task['task_id'])] = result

                        results[job_id] = worker_task_map

                return Response(results)

            return Response({"error": "User is not authorized for this call."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"error": "Missing minimum search parameter 'job_id' in the call."}, status=status.HTTP_400_BAD_REQUEST)


class WorkersEngagedView(APIView):
    """
    View to get the details of the workers engaged with a job.

    * Requires token authentication.
    * Only manager and the owner of the job may access this view.
    """
    permission_classes = (And(IsAuthenticated, Or(IsManager, IsSearcher)), )

    def get(self, request):
        if request.GET and 'job_id' in request.GET:
            results = {}

            # filter parameters
            jobs = []

            for key, vals in dict(request.GET).items():
                if key == 'job_id':
                    jobs.extend([re.match(r'(^[a-zA-Z0-9]{8})', elem).group(1) for elem in vals if re.match(r'(^[a-zA-Z0-9]{8})', elem)])

            if not jobs:
                return Response({"error": "Invalid or no job_id's specified."}, status=status.HTTP_400_BAD_REQUEST)

            for job_id in jobs:
                try:
                    job = Job.fetch_job(job_id=job_id)
                except KeyError:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                except ValueError:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                if user_is_manager(request) or \
                        (user_is_searcher(request) and request_from_user(request, job['job_owner'])):

                    workers = set()

                    for task_id in job['job_wots'] + job['job_qats']:
                        task = Task.fetch_task(task_id=task_id)
                        for worker in task['results'].keys():
                            workers.add(worker)

                    for worker in list(workers):
                        worker_details = {}

                        try:
                            user = User.objects.get(id=int(worker))
                            worker_details['username'] = user.username
                            worker_details['email']    = user.email
                        except User.DoesNotExist:
                            return Response({'error': "Worker with id '%s' is not registered." % worker},
                                            status=status.HTTP_204_NO_CONTENT)

                        try:
                            user_details = UserInformation.objects.get(user_id=int(worker))
                            worker_details['first_name']    = user_details.first_name
                            worker_details['last_name']     = user_details.last_name

                        except UserInformation.DoesNotExist:
                            pass

                        results[worker] = worker_details

            return Response(results)

        return Response({"error": "Missing minimum search parameter 'job_id' in the call."}, status=status.HTTP_400_BAD_REQUEST)


class QATView(APIView):
    """
    View to get the annotations in a json format to be used further as QATs for another job.

    * Requires token authentication.
    * Only the owner of the job may access this view.
    """
    permission_classes = (IsAuthenticated, IsSearcher)

    def get(self, request):
        if request.GET and 'job_id' in request.GET:
            results = {"qats": []}

            # filter parameter
            jobs = []
            for key, vals in dict(request.GET).items():
                if key == 'job_id':
                    jobs.extend([re.match(r'(^[a-zA-Z0-9]{8})', elem).group(1) for elem in vals if re.match(r'(^[a-zA-Z0-9]{8})', elem)])

            if not jobs:
                return Response({"error": "Invalid or no job_id's specified."}, status=status.HTTP_400_BAD_REQUEST)

            for job_id in jobs:
                try:
                    job = Job.fetch_job(job_id=job_id)
                except KeyError:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                except ValueError:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                if user_is_searcher(request) and request_from_user(request, job['job_owner']):
                    for task_id in job['job_qats']:
                        task = Task.fetch_task(task_id=task_id)
                        qat = dict()
                        qat['image_url'] = task['image_url']
                        qat['result']    = task['result']
                        results["qats"].append(qat)

            return Response(results)

        return Response({"error": "Missing minimum search parameter 'job_id' in the call."},
                        status=status.HTTP_400_BAD_REQUEST)
