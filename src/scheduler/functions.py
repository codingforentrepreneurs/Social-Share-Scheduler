import inngest

from .client import inngest_client


# Create an Inngest function
@inngest_client.create_function(
    fn_id="post_scheduler",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="posts/post.scheduled"),
)
def post_scheduler(ctx: inngest.Context) -> str:
    print(ctx.event)
    return "done"
