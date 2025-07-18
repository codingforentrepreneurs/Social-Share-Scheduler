from django.utils import timezone

import inngest

from .client import inngest_client


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
    try:
        instance = Post.objects.get(id=object_id)
    except Post.DoesNotExist:
        return "missing"
    share_platforms = instance.get_scheduled_platforms()
    if "linkedin" in share_platforms:
        # handle linkedin
        try:
            instance.verify_can_share_on_linkedin()
        except Exception as e:
            print("error")
            return "Problem saving instance"
        instance = instance.perform_share_on_linkedin(mock=True, save=False)
        print(share_platforms, instance.user, str(instance.content)[:10])

    instance.share_complete_at = timezone.now()
    instance.save()
    return "done"
