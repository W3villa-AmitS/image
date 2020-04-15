from math import ceil
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from celery import shared_task

from .models import Task, Job

from .service_calls import AnnotationAnalysisAndProcessingApi
from .service_calls import ResponseError, ConnectivityError, URLError


#
# helper functions
#
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


def validate_json(content):
    try:
        AnnotationAnalysisAndProcessingApi.validate(content)
    except ResponseError as err:
        raise ValidationError(err.args[0])
    except ConnectivityError:
        raise ValidationError("Microservice Error: Problems in connectivity.")
    except URLError:
        raise ValidationError("Microservice Error: Invalid URL requested.")


def validate_boxing_type(boxing_type, content):
    try:
        AnnotationAnalysisAndProcessingApi.validate_boxing_type(boxing_type, content)
    except ResponseError as err:
        raise ValidationError(err.args[0])
    except ConnectivityError:
        raise ValidationError("Microservice Error: Problems in connectivity.")
    except URLError:
        raise ValidationError("Microservice Error: Invalid URL requested.")


def _qats_required(initial_qats, number_of_wots, qat_frequency):
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


def _more_qats_required(job_id):
    job = Job.fetch_job(job_id)

    # calculate the required number of QATs
    total_qats_required = _qats_required(job['job_initial_qats'],
                                         job['job_number_of_wots'],
                                         job['job_qat_frequency'])

    return total_qats_required - job['job_number_of_qats']


def _validate_qat(job, qat):
    try:
        URLValidator()(qat['image_url'])
    except ValidationError:
        raise AssertionError("Specified invalid image_url: '%s'" % qat['image_url'])

    try:
        validate_json(qat['result'])
    except ValidationError:
        raise AssertionError("Specified invalid annotation data.")

    # check only for the picture boxing type of jobs and that too if opted for fixed boxing type
    if job['job_type'] == 'P' and job['job_boxing_type']:
        try:
            validate_boxing_type(job['job_boxing_type'], qat['result'])
        except ValidationError:
            raise AssertionError("Specified invalid boxing type.")

    #
    # check if attributes specified during job creation are in match with the result provided
    #
    job_attributes = get_attributes(job['job_attributes'])

    attributes_delta = set(job_attributes) - set(qat['result'].keys())
    if attributes_delta:
        raise AssertionError("Attributes in result mismatched with job attributes.")

    job_attributes = get_attributes(job['job_attributes'])

    attributes_delta = set(job_attributes) - set(qat['result'].keys())
    if attributes_delta:
        raise AssertionError("Missing attribute(s) in qat: '%s'" %(", ".join(attributes_delta)) )


def _validate_job(job_id):
    try:
        return Job.fetch_job(job_id)
    except (KeyError, ValueError) as err:
        raise AssertionError(err.args[0])


def _add_qat(job_id, qat):
    task = Task(job_id=job_id,
                image_url=qat['image_url'],
                is_qat=True,
                result=qat['result'],
                results={},
                max_occurrence=0)
    task.save()

     # update qat id
    Job.add_qat(job_id=job_id, qat_id=task.task_id)

    # update the count of quality assessment tasks added
    Job.update_qat_count(job_id = job_id, count=1)

    return task


def generate_qat(job_id, qat):
    if _more_qats_required(job_id=job_id) > 0:

        job = _validate_job(job_id)

        _validate_qat(job, qat)
        qat = _add_qat(job_id, qat)

        # update qats_status
        Job.update_qats_status(job_id=job_id, new_status="qats_added")

        if job['job_wot_status'] == 'wots_added' and _more_qats_required(job_id=job_id) <= 0:
            # update the status of job
            Job.update_status(job_id=job_id, new_status="finalized")

        return qat

    return {}

@shared_task
def generate_wots(csv_file, job_id, max_occurrence):
    try:
        _validate_job(job_id)
    except AssertionError:
        return {}
    added_wots    = 0
    rejected_wots = 0

    # set wots_status to mark it in an intermediate state
    Job.update_wots_status(job_id=job_id, new_status="being_added")

    for index, image_url in enumerate(csv_file, start=1):
        image_url = str(image_url).strip()

        try:
            URLValidator()(image_url)
        except ValidationError:
            print("-> Skipped WOT because of invalid URL '%s'." % image_url)
            rejected_wots += 1
            continue

        # Task( job_id=job_id,
        #       image_url=image_url,
        task = Task(  job_id=job_id,
                      image_url=image_url,

                    # # considering WOT
                    # is_qat=False,
                    # results={},
                    # max_occurrence=max_occurrence
                    # ).save()
                       # considering WOT
                        is_qat=False,
                        results={},
                        max_occurrence=max_occurrence
                        )
        task.save()     

        added_wots += 1

        # update qat id
        Job.add_wot(job_id=job_id, wot_id=task.task_id)

    # update the actual count of wots added
    wot_count = len([t for t in Task.fetch_all_tasks_from_job(job_id=job_id) if t['is_qat'] is False])
    Job.update_exact_wot_count(job_id=job_id, count=wot_count)

    try:
        job = Job.fetch_job(job_id=job_id)
    except (KeyError, ValueError) as err:
        raise AssertionError(err.args[0])

    # update wots_status
    Job.update_wots_status(job_id=job_id, new_status="wots_added")

    if job['job_qat_status'] == 'qats_added' and _more_qats_required(job_id=job_id) <= 0:
        # update the status of job
        Job.update_status(job_id=job_id, new_status="finalized")

    print("-> Out of given '%d' WOTs, '%d' WOTs added to job with job_id '%s' successfully." % (index, added_wots, job_id))
    return {
            "job_id"           : job_id,
            "urls_given"       : len(csv_file),
            "urls_rejected"    : rejected_wots,
            "urls_added"       : added_wots
            }

@shared_task
def generate_qats(job_id, qats):
    try:
        job = _validate_job(job_id)
    except AssertionError:
        return {}

    added_qats    = 0
    rejected_qats = 0

    for index, qat in enumerate(qats, start=1):
        if _more_qats_required(job_id=job_id) <= 0:
            print ('-> QAT requirement fulfilled.')
            break

        try:
            _validate_qat(job, qat)
        except AssertionError as err:
            print ("-> Skipped QAT '%d'. %s" % (index, err))
            rejected_qats += 1
            continue

        _add_qat(job_id, qat)
        added_qats += 1

    try:
        job = Job.fetch_job(job_id=job_id)
    except (KeyError, ValueError) as err:
        raise AssertionError(err.args[0])

    # update qats_status
    Job.update_qats_status(job_id=job_id, new_status="qats_added")

    if job['job_wot_status'] == 'wots_added' and _more_qats_required(job_id=job_id) <= 0:
        # update the status of job
        Job.update_status(job_id=job_id, new_status="finalized")

    print("-> Out of given '%d' QATs, '%d' QATs added to job with job_id '%s' successfully." % (len(qats), added_qats, job_id))
    return {
            "job_id"           : job_id,
            "qats_given"       : len(qats),
            "qats_processed"   : index,
            "qats_rejected"    : rejected_qats,
            "qats_added"       : added_qats,
            "qats_leftover"    : len(qats) - index
            }

@shared_task
    
def extract_qats_and_wots(job_id): 
    wots = []
    qats = []
    for task in Task.fetch_all_tasks_from_job(job_id=job_id):
       
        if task['is_qat']:
            qats.append(task['task_id'])
        else:
            wots.append(task['task_id'])

      

    Job.update_qats_and_wots(job_id=job_id, wots=wots, qats=qats)
    Job.update_status(job_id=job_id, new_status='approved')

