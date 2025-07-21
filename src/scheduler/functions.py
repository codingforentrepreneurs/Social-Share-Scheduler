from datetime import timedelta
from django.utils import timezone

import inngest

from .client import inngest_client


def workflow_share_on_linkedin_node(instance):
    try:
        instance.verify_can_share_on_linkedin()
    except Exception as e:
        print("error")
        return False, "Did not share on linkedin"
    # ctx.step.sleep("linkedin-sleeper", timedelta(seconds=7))
    instance = instance.perform_share_on_linkedin(mock=True, save=False)
    # print(share_platforms, instance.user, str(instance.content)[:10])
    return True, "Shared on linkedin"


# Create an Inngest function
@inngest_client.create_function(
    fn_id="post_scheduler",
    # Event that triggers this function
    trigger=inngest.TriggerEvent(event="posts/post.scheduled"),
)
def post_scheduler(ctx: inngest.Context) -> str:
    print(ctx.event.data)
    from posts.models import Post
    object_id = ctx.event.data.get("object_id")
    qs = Post.objects.filter(id=object_id)
    if not qs.exists():
        return "missing"
    instance = qs.first()
    qs.update(share_start_at = timezone.now())
    share_platforms = instance.get_scheduled_platforms()
    if "linkedin" in share_platforms:
        # handle linkedin
        # ctx.step.sleep("linkedin-sleeper", 7 * 1000)
        publish_date = timezone.now() + timedelta(seconds=3)
        if instance.share_at:
            publish_date = instance.share_at + timedelta(seconds=3)
        # ctx.step.sleep("linkedin-sleeper", timedelta(seconds=7))
        ctx.step.sleep_until("linkedin-sleeper-schedule", publish_date)
        ctx.step.run("linkedin-share-workflow-step", lambda: workflow_share_on_linkedin_node(instance))
        

    
    qs.update(share_complete_at = timezone.now())
    # instance.share_complete_at = timezone.now()
    # instance.save()
    return "done"
