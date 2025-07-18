import inngest

from .client import inngest_client


# Create an Inngest function
@inngest_client.create_function(
    fn_id="my_function",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="app/my_function"),
)
def my_function(ctx: inngest.Context) -> str:
    print(ctx.event)
    return "done"


@inngest_client.create_function(
    fn_id="another_func",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="app/my_function"),
)
def another_func(ctx: inngest.Context) -> str:
    print('event again', ctx.event)
    return "done"