from random import shuffle, choice
from math import ceil

from django.utils import timezone

from users.models import Worker, TaskCompleted, TaskAllocation
from jobs.models  import Job, Task

class ModelError(Exception):
    """
    All model related errors.
    """
    def __init__(self, *args):
        super(ModelError, self).__init__(*args)

class WorkerActiveOnMultipleJobs(ModelError):
    """
    Exception if worker active on multiple jobs.
    """
    def __init__(self, *args):
        super(WorkerActiveOnMultipleJobs, self).__init__(*args)

class WorkerAlreadyActive(ModelError):
    """
    Exception if worker already active on another job.
    """
    def __init__(self, *args):
        super(WorkerAlreadyActive, self).__init__(*args)

class WorkerDisqualifiedOnJob(ModelError):
    """
    Exception if worker is disqualified on a job.
    """
    def __init__(self, *args):
        super(WorkerDisqualifiedOnJob, self).__init__(*args)

def _get_next_task_type(completed_tasks, initial_qats, number_of_wots, qat_frequency):
    """
    Todo:
    :param completed_tasks:
    :param initial_qats:
    :param number_of_wots:
    :param qat_frequency:
    :return:
    """
    order = ""

    # add initial QATs
    for i in range(initial_qats):
        order += 'Q'

    # add some WOTS
    for i in range(1, number_of_wots + 1):
        order += 'W'

        # add intermittent QATs
        if i % qat_frequency == 0:
            order += "Q"

    # remove any QAT if scheduled at the end of the order
    if order.endswith('Q'):
        order = order[:-1]

    if completed_tasks < len(order):
        return order[completed_tasks]
    return None

def _get_random_task(tasks, task_type, user_id):
    """
    Todo:
    :param tasks:
    :param task_type:
    :param user_id:
    :return:
    """
    shuffle(tasks)
    for task in tasks:
        task = Task.fetch_task(task)
        if str(user_id) not in task['results'].keys():
            if task_type == 'W' and len(task['results']) < int(task['max_occurrence']):
                return task
            elif task_type == 'Q':
                return task
            else:
                return None
    return None

def _get_a_task(job, user_id, next_task_type):
    """
    Todo:
    :param job:
    :param user_id:
    :param next_task_type:
    :return:
    """
    wots = job['job_wots']
    qats = job['job_qats']

    number_of_initial_qats = job['job_initial_qats']
    qat_frequency = job['job_qat_frequency']

    required_qats = number_of_initial_qats + ceil((len(wots) / qat_frequency)) - 1

    assert len(qats) >= required_qats, \
        "To fulfill initial QATs(%d) and the specified frequency of the intermittent QATs(%d), job is short of '%d' QATs." % (
            number_of_initial_qats, qat_frequency, required_qats - len(qats))

    if next_task_type == 'Q':
        return _get_random_task(qats, next_task_type, user_id)

    elif next_task_type == 'W':
        return _get_random_task(wots, next_task_type, user_id)


class TaskScheduler(object):
    @classmethod
    def get_next_task(cls, job_id, user_id):
        """
        Todo:
        :param job_id:
        :param user_id:
        :return:
        """
        # get list of worker activation on jobs
        worker_activation = list(Worker.objects.filter(is_active=True, user_id=int(user_id)))

        if worker_activation:
            if len(worker_activation) > 1:
                raise WorkerActiveOnMultipleJobs("Worker active on multiple jobs")
                # ideally this case must never happen

            #
            # disallow worker if already active on another Job
            #
            if worker_activation[0].job_id != job_id:
                raise WorkerAlreadyActive("Worker already active on another job.", worker_activation[0].job_id)

        # check worker allocation on this job
        worker_allocation = Worker.objects.filter(job_id=job_id, user_id=int(user_id))

        # check worker disqualification for this job
        if worker_allocation:
            if len(worker_allocation) > 1:
                raise WorkerActiveOnMultipleJobs("Worker allocated on multiple jobs")
                # ideally this case must never happen

            # if user disqualified before on this task
            disqualified_till = worker_allocation[0].disqualified_till
            if disqualified_till and timezone.now() < worker_allocation[0].disqualified_till:
                raise WorkerDisqualifiedOnJob("Worker can't reattempt to work on job with job_id '%s', till %s" % (
                job_id, disqualified_till))

        #
        # activate worker if not active on this job
        #
        if worker_allocation and not worker_activation:
            worker_allocation[0].is_active = True
            worker_allocation[0].save()

        #
        # check if last allocated task is completed by worker
        #
        if worker_allocation:
            last_allocation = worker_allocation[0].task_allocated
            if last_allocation and not last_allocation in worker_allocation[0].tasks_completed:
                task = Task.fetch_task(last_allocation)

                # check if task is not completed (WOT)
                if task['is_qat'] or len(task['results']) < int(task['max_occurrence']):
                    return task

        #
        # maintain an entry in table to monitor the worker activation and accuracy
        #
        if worker_allocation:
            worker_allocation = worker_allocation[0]
        else:
            # create and entry in Worker table
            worker_allocation = Worker.objects.create(job_id=job_id, user_id=int(user_id), is_active=True)
            worker_allocation.save()

        #
        # get a task for user
        #

        # 1. Get all tasks done by worker from tasks completed table
        tasks_completed_by_worker = [t.task_id for t in TaskCompleted.objects.filter(user_id=int(user_id), job_id=job_id)]

        # 2. fetch job relevant details
        job = Job.fetch_job(job_id=job_id)

        next_task_type = _get_next_task_type(len(tasks_completed_by_worker),
                                            int(job["job_initial_qats"]),
                                            int(job["job_number_of_wots"]),
                                            int(job["job_qat_frequency"]))

        if next_task_type is None:
            return None

        task = _get_a_task(job, user_id, next_task_type)

        if task:
            # 3. make an entry in task allocation table
            task_allocation = TaskAllocation.objects.filter(task_id=task['task_id'], job_id=job['job_id'])

            if task_allocation:
                task_allocation = task_allocation[0]
            else:
                task_allocation = TaskAllocation.objects.create(task_id=task['task_id'], job_id=job['job_id'])

                # also update the status of the job
                if job['job_status'] == "approved":
                    Job.update_status(job_id=job_id, new_status='in_progress')

            task_allocation.worker_list.append(int(user_id))
            task_allocation.save()

            worker_allocation.task_allocated = task['task_id']
            worker_allocation.save()

        return task
