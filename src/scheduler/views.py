import inngest
import inngest.django 

from .client import inngest_client
from .functions import (
    my_function
)



scheduler_inngest_view_path = inngest.django.serve(inngest_client, [my_function])