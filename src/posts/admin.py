from django.contrib import admin

# Register your models here.
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_filter = ['updated_at',]
    # list_display = ['content', 'updated_at']

    def get_list_display(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return ['content', 'user',  'updated_at']
        return ['content', 'updated_at']

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_delete_permission(self, request, obj=None, *args, **kwargs):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        return obj.user == request.user and not obj.shared_at_linkedin

    def get_readonly_fields(self, request, obj, *args, **kwargs):
        if obj and obj.shared_at_linkedin:
            return ["user", "content", "shared_at_linkedin", "share_on_linkedin"]
        if request.user.is_superuser:
            return ["shared_at_linkedin",]
        return ["user", "shared_at_linkedin",]

    def save_model(self, request, obj, form, change):
        if not change: # the obj no change, aka being created
            if not obj.user:
                obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Post, PostAdmin)