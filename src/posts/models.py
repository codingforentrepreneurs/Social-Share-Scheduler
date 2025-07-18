from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from helpers import linkedin

import inngest
from scheduler.client import inngest_client

User = settings.AUTH_USER_MODEL # "auth.User"

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    share_now = models.BooleanField(default=None, null=True, blank=True)
    share_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    share_complete_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    share_on_linkedin = models.BooleanField(default=False)
    shared_at_linkedin = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if self.share_now is None and self.share_at is None:
            raise ValidationError(
                {
                    "share_at": "You must select a time to share or share it now",
                    "share_now": "You must select a time to share or share it now"
                }
            )
        if self.share_on_linkedin:
            self.verify_can_share_on_linkedin()
        # run the save method (pre & post save)

    def schedule_platforms(self):
        platforms = []
        if self.share_on_linkedin:
            platforms.append("linkedin")
        return platforms

    def save(self, *args, **kwargs):
        # pre-save
        do_schedule_post = False
        if all([
            self.share_now is not None or self.share_at is not None,
            self.share_complete_at is None
        ]):
            do_schedule_post = True
        super().save(*args, **kwargs)

        if do_schedule_post:
            inngest_client.send_sync(
                inngest.Event(
                    name="posts/post.scheduled",
                    id=f"posts/post.scheduled.{self.id}",
                    data={"object_id": self.id}
                )
            )
        # post-save

    def perform_share_on_linkedin(self, save=False):
        self.share_on_linkedin = False
        if self.shared_at_linkedin:
            return
        try:
            linkedin.post_to_linkedin(self.user, self.content)
        except:
            raise ValidationError({
                "content": "Could not share to linkedin."
            })
        self.shared_at_linkedin = timezone.now()
        if save:
            self.save()
        return self
    
    def verify_can_share_on_linkedin(self):
        # run validation errors if attempting to share on linkedin
        if len(self.content) < 5:
            raise ValidationError({
                "content": "Content must be at least 5 characters long."
            })
        if self.shared_at_linkedin:
            raise ValidationError({
                "share_on_linkedin": f"Content is already shared on LinkedIn at {self.shared_at_linkedin}.",
                "content": "Content is already shared on LinkedIn."
            })
        try:
            linkedin.get_linkedin_user_details(self.user)
        except linkedin.UserNotConnectedLinkedIn:
            raise ValidationError({
                "user": f"You must connect LinkedIn before sharing to LinkedIn."
            })
        except Exception as e:
            raise ValidationError({
                "user": f"{e}"
            })