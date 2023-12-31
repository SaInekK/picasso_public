from celery import shared_task

from processing.services import FileProcessService


@shared_task(bind=True,
             autoretry_for=(Exception,),
             retry_backoff=True,
             retry_kwargs={'max_retries': 2})
def process_uploaded_file(self, file_id):
    service = FileProcessService(file_id)
    service.process_file()

    return 'success'
