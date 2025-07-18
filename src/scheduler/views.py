import inngest
import inngest.django 

from .client import inngest_client
from .functions import (
    post_scheduler
)


active_inngest_functions = [
    post_scheduler
]


scheduler_inngest_view_path = inngest.django.serve(inngest_client, active_inngest_functions)