from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from helpers import linkedin

User = settings.AUTH_USER_MODEL # "auth.User"

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    share_on_linkedin = models.BooleanField(default=False)
    shared_at_linkedin = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if len(self.content) < 5:
            raise ValidationError({
                "content": "Content must be at least 5 characters long."
            })
        elif self.share_on_linkedin and not self.can_share_on_linkedin:
            raise ValidationError({
                "share_on_linkedin": f"Content is already shared on LinkedIn at {self.shared_at_linkedin}.",
                "content": "Content is already shared on LinkedIn."
            })

    def save(self, *args, **kwargs):
        # pre-save
        if self.share_on_linkedin and self.can_share_on_linkedin:
            print("sharing on linkedin")
            try:
                linkedin.post_to_linkedin(self.user, self.content)
            except:
                raise ValidationError({
                    "content": "Could not share to linkedin."
                })
            self.shared_at_linkedin = timezone.now()
        else:
            print('not sharing')
        self.share_on_linkedin = False
        super().save(*args, **kwargs)
        # post-save

    @property
    def can_share_on_linkedin(self):
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
            # return False
        return not self.shared_at_linkedin