import re
import csv, io
from datetime import timedelta

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import NotFound, NotAcceptable

from users.models import Worker, TaskAllocation, TaskCompleted
from .models import Job, Task
from .tasks import generate_wots, generate_qat, generate_qats

from .service_calls import AnnotationAnalysisAndProcessingApi
from .service_calls import ExternalMicroServiceError, ResponseError, ConnectivityError, URLError

DEBUG = settings.DEBUG

#
# helper functions
#
def comma_separated_string(value):
    """
    Validate the specified string to be in csv format.
    :param value: string to be validated
    :exception ValidationError: string is not in csv format.
    """
    if re.search(r"[^a-z0-9,_ .]", value, re.I):
        raise serializers.ValidationError(
            "Comma separated words made up of characters other than of 'a-zA-Z0-9_' are not allowed.")

def in_grade(value, grade):
    """
    todo:
    :param value:
    :param grade:
    :return:
    """
    if grade == 'A':
        return value >= 0.9
    elif grade == 'B':
        return value >= 0.8
    elif grade == 'C':
        return value >= 0.7
    elif grade == 'D':
        return value >= 0.6
    elif grade == 'E':
        return value >= 0.3
    raise NotAcceptable("E5096: Should never reach here.")

def get_attributes(csv_string):
    """
    ToDo
    :param csv_string:
    :return:
    """
    result = []
    for attr in csv_string.split(','):
        if attr.strip():
            result.append(attr.strip())
    return result

def get_number_of_lines(csv_file):
    """
    Calculate the number of lines in the file, excluding the
    header line.
    Assumed header line as 'image_url' and each non-empty line
    other than header contain valid single url.
    :param csv_file: csv_file in memory
    :return: number of non-empty lines in file assuming each file
    representing a url.
    """
    csv_file.seek(0)
    fileContent = csv_file.read().decode('utf-8')
    index = 0
    for line in fileContent.split('\n'):
        if line.strip() and not line.strip().startswith('image_url') and not line.strip() == '[object Object]':
                index+=1
    return index

def json_validator(content):
    try:
        AnnotationAnalysisAndProcessingApi.validate(content)
    except ResponseError as err:
        raise serializers.ValidationError(err.args[0])
    except ConnectivityError:
        raise serializers.ValidationError("Microservice Error: Problems in connectivity.")
    except URLError:
        raise serializers.ValidationError("Microservice Error: Invalid URL requested.")


def validate_boxing_type(boxing_type, content):
    try:
        AnnotationAnalysisAndProcessingApi.validate_boxing_type(boxing_type, content)
    except ResponseError as err:
        raise serializers.ValidationError(err.args[0])
    except ConnectivityError:
        raise serializers.ValidationError("Microservice Error: Problems in connectivity.")
    except URLError:
        raise serializers.ValidationError("Microservice Error: Invalid URL requested.")


class JobSerializer(serializers.Serializer):
    """
    Serializer Class for Job related fields.
    Expect following fields:

    :internal:
        job_id                  character
        job_owner               integer
        job_status              character

    :user defined:
        job_name                character
        job_type                character
        job_attributes          character
        job_description         character
        job_instructions        character
        job_max_occurrence      integer
        job_criteria_age_min    integer
        job_criteria_age_max    integer
        job_criteria_gender     list
        job_criteria_location   character
        job_criteria_grade      character
        job_initial_qats        integer
        job_qat_frequency       integer
    """
    status_choices = [ "initialized",          # a freshly created job
                       "being_created",        # Celery is scheduled to add multiple QATS/WOTS asynchronously
                       "finalized",            # QAT condition met
                       "approved",             # job approved by a manager
                       "disapproved",          # job disapproved by a manager
                       "in_progress",          # job is in-progress
                       "completed",            # job is completed by workers
                       "validated",            # job is validated by searcher
                       "rejected" ,             # job results are discarded by searcher
                        "approving"
                    ]

    type_choices = [
        ('P', 'Picture Boxing'),
        ('S', 'Specific Points'),
        ('A', 'Attributes'),
    ]

    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('T', 'Transgender')
    ]

    grade_choices = [
        ('A', 'above 90%'),
        ('B', 'above 80%'),
        ('C', 'above 70%'),
        ('D', 'above 60%'),
        ('E', 'below 60%'),
    ]

    boxing_type_choices = ["Rectangle", "Square", "Polygon"]

    job_id                = serializers.CharField           (max_length=8, allow_blank=False, read_only=True)
    job_owner             = serializers.IntegerField        (read_only=True)
    job_status            = serializers.ChoiceField         (choices=status_choices, read_only=True)
    job_name              = serializers.CharField           (max_length=256, allow_blank=False)
    job_type              = serializers.ChoiceField         (choices=type_choices, allow_blank=False)
    job_attributes        = serializers.CharField           (max_length=256, allow_blank=False,
                                                             validators=[comma_separated_string])
    job_description       = serializers.CharField           (max_length=512, allow_blank=False )
    job_instructions      = serializers.CharField           (max_length=256, allow_blank=False)
    job_max_occurrence    = serializers.IntegerField        (min_value=1)
    job_criteria_age_min  = serializers.IntegerField        (min_value=18, max_value=100)
    job_criteria_age_max  = serializers.IntegerField        (min_value=19, max_value=100)
    job_criteria_gender   = serializers.MultipleChoiceField (choices=gender_choices, allow_blank=False)
    job_criteria_location = serializers.CharField           (max_length=100, allow_blank=False,
                                                             validators=[comma_separated_string])
    job_criteria_grade    = serializers.ChoiceField         (choices=grade_choices, allow_blank=False)
    job_initial_qats      = serializers.IntegerField        (min_value=0)
    job_qat_frequency     = serializers.IntegerField        (min_value=0)

    job_boxing_type       = serializers.ChoiceField         (choices=boxing_type_choices, default=None)

    def create(self, validated_data):
        # check if min and max ages are specified correctly
        if int(validated_data['job_criteria_age_min']) >= int(validated_data['job_criteria_age_max']):
            raise AssertionError("Minimum specified age can't be equal or greater than specified maximum age.")

        # if not specified default the job_boxing_type as rectangle
        if validated_data['job_type'] is 'P' and validated_data['job_boxing_type'] is None:
            raise AssertionError("Missing 'job_boxing_type' for 'Picture Boxing' type of job. ")

        # create and post job on database
        job = Job(**validated_data)
        job.save()
        return job


class AddWOTSerializer(serializers.Serializer):
    """
    Serializer Class for addition of Tasks to a Job.
    Expect following fields:

    :user defined:
        csv_file                file
    """
    csv_file = serializers.FileField(required=False)

    def _convert_to_json(self, csv_file):
        result = []
        csv_file.seek(0)
        for row in csv.DictReader(io.StringIO(csv_file.read().decode('utf-8'))):
            result.append(row['image_url'])
        return result

    def create(self, validated_data):
        #
        # check if necessary fields are provided
        #
        for elem in ['csv_file', 'job_id', 'max_occurrence']:
            assert elem in validated_data, "Missing '%s' in the request." % elem

        # assuming all the urls in csv file as correct
        number_of_tasks = get_number_of_lines(validated_data['csv_file'])

        # update the number of WOTs on the basis of total number of lines in csv file
        Job.update_wot_count(job_id=validated_data['job_id'], count=number_of_tasks)

        # put an interim status of job
        Job.update_status(job_id=validated_data['job_id'], new_status='being_created')

        try:
            generate_wots.delay(   self._convert_to_json(validated_data['csv_file']),
                                   validated_data['job_id'],
                                   validated_data['max_occurrence'])
        except ValidationError as err:
            raise AssertionError(err.args[0])


        # Note: No task is created as of now. All the tasks shall be created in another
        # process asynchronously, so it is not possible to determine the created tasks
        # hence returning an empty list.
        return []


class AddQATSerializer(serializers.Serializer):
    """
    Serializer class to add a list of QATs.
    Expect following fields:

    :user defined:
        qats
    """
    qats = serializers.JSONField()

    def create(self, validated_data):
        #
        # check if necessary fields are provided
        #
        for elem in ['qats', 'job_id']:
            assert elem in validated_data, "Missing '%s' in the request." % elem

        if len(validated_data['qats']) > 1:
            # schedule generation of QATs asynchronously
            generate_qats.delay(validated_data['job_id'], validated_data['qats'])

            # Note: No task is created as of now. All the tasks shall be created in another
            # process asynchronously, so it is not possible to determine the created tasks
            # hence returning an empty list.
            return []

        else:
            return generate_qat(validated_data['job_id'], validated_data['qats'][0])


class AddResultSerializer(serializers.Serializer):
    """
    Serializer Class for result posting related fields.
    Expect following fields:

    :user defined:
        result                json
    """
    result = serializers.JSONField(validators=[json_validator, ])

    def update(self, instance, validated_data, user_id):
        #
        # check if user is active on this job
        #
        worker = Worker.objects.get(job_id=instance['job_id'], user_id=int(user_id))
        if not (worker and worker.is_active):
            raise NotAcceptable("Worker not active on job with job_id '%s'"% instance['job_id'])

        #
        # check if user is posting result against allocation
        #
        if worker and not worker.task_allocated == instance['task_id']:
            raise NotAcceptable("Submission against not-allocation is not allowed")


        #
        # check if same user has attempted to post result again
        #
        if TaskCompleted.objects.filter(task_id=instance['task_id'], user_id=int(user_id)):
            raise NotAcceptable("Re-submission of the result for the same task is not allowed.")

        #
        # validate the boxing type for all the annotations if it was opted to fix the boxing type
        #
        try:
            job = Job.fetch_job(instance['job_id'])
        except (KeyError, ValueError) as err:
            raise AssertionError(err.args[0])

        # get the boxing type from the job
        boxing_type = job['job_boxing_type']

        # check only for the picture boxing type of jobs and that too if opted for fixed boxing type
        if job['job_type'] == 'P' and boxing_type:
            try:
                validate_boxing_type(boxing_type, validated_data['result'])
            except serializers.ValidationError as err:
                raise AssertionError(err.args[0])

        #
        # check if attributes specified during job creation are in match with the result provided
        #
        job_attributes = get_attributes(job['job_attributes'])

        if set(job_attributes) - set(validated_data['result'].keys()):
            raise AssertionError("Attributes in result mismatched with job attributes.")

        #
        # Process the result as per the type of the task i.e. QAT or WOT
        #
        if instance['is_qat']:
            # being QAT there must be a searcher data for the task in the job
            try:
                response = AnnotationAnalysisAndProcessingApi.qualify(instance['result'], validated_data['result'])
            except (ResponseError, ExternalMicroServiceError) as err:
                raise NotFound("Microservice Error: " + err.args[0])

            qat_passed = True if response['result'] == "passed" else False

            #
            # update accuracy of the worker on this job
            #
            if qat_passed:
                worker.qat_passed += 1
            else:
                worker.qat_failed += 1
            worker.save()

            #
            # Check for worker accuracy
            # if fall below required accuracy revert all WOT result submissions till last successful QAT
            #

            # 1. check if worker is not doing initial set of QAT
            number_of_initial_qats = job["job_initial_qats"]

            tasks_completed = worker.tasks_completed[:]

            worker_accuracy = worker.qat_passed / (worker.qat_passed + worker.qat_failed)

            # 2. check if worker qualifies the expected standards for the job
            disqualified = None

            # exempt worker rejection during the initial set of QATs
            if len(tasks_completed) > int(number_of_initial_qats):
                #
                # 3. if accuracy falls below expectation, disqualify worker on this job for a day
                #
                if not in_grade(worker_accuracy, job["job_criteria_grade"]):
                    delta = timedelta(days=1)

                    worker.disqualified_till = timezone.now() + delta
                    worker.save()

                    #
                    # 4. roll back all the results submitted by worker till last QAT check
                    #
                    for task_id in tasks_completed[::-1]:
                        task = Task.fetch_task(task_id)

                        if task['is_qat']:
                            break

                        Task.rollback_result(task_id, int(user_id))

                        # remove any entry of attempt from record
                        worker.tasks_completed.remove(task_id)
                        worker.save()

                        # remove any entry from completed jobs
                        completed_tasks = TaskCompleted.objects.filter(task_id=task_id, user_id=int(user_id))
                        if DEBUG:
                            assert len(completed_tasks) == 1, "Multiple entries for the completion of task '%s' by user '%d' in database" % (task_id, int(user_id))

                        completed_tasks[0].delete()

                    disqualified = "Worker accuracy fall below job expectations, hence worker disqualified on the job."

                    # disengage worker from this job
                    worker.is_active = False
                    worker.save()

            return_dict = dict(task='qat', accuracy='%0.2f%%' % (100 * worker_accuracy))
            return_dict['status'] = disqualified if disqualified else ('passed' if qat_passed else 'failed')

        else:
            return_dict = dict(task='wot', status='submitted')

        # clear the task allocation table
        allocation = TaskAllocation.objects.filter(task_id=instance['task_id'])
        if DEBUG:
            assert len(allocation) == 1, "Multiple entries for allocations for task '%s' in database"% instance['task_id']
        allocation[0].worker_list.remove(int(user_id))
        allocation[0].save()

        #
        # check if a WOT is already completed
        #
        if not instance['is_qat'] and Task.completed(instance):
            raise NotAcceptable("Task already completed.")

        # all the posted results for the task
        results = instance['results']

        results["%s" % user_id] = validated_data['result']

        try:
            Task.update_results(task_id=instance['task_id'], updated_results=results)
        except KeyError:
            raise NotFound

        # a. mark the submission of the result for the task by this user
        worker.tasks_completed.append(instance['task_id'])
        worker.save()

        # b. mark the submission of the result for the task by this user
        TaskCompleted.objects.create(user_id=int(user_id), task_id=instance['task_id'], job_id=instance['job_id'])

        #
        # check if task is completed and if job is completed
        #
        if not instance['is_qat'] and Task.completed(instance) and Job.completed(instance['job_id']):
            Job.update_status(instance['job_id'], "completed")

        # get task statistics
        task_stats = {
                        'tasks_completed': '%d' % len(worker.tasks_completed),
                        'total_tasks': '%d' % len(job['job_wots'] + job['job_qats'])
                      }

        if DEBUG:
            return dict(return_dict, **task_stats)

        return task_stats
