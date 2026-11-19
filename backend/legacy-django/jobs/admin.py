from django.contrib import admin, messages
from .models import (
    Application,
    Company,
    ContactInquiry,
    Interview,
    Job,
    JobAlert,
    JobAlertPreference,
    Notification,
    Profile,
    SavedJob,
    SignupRecord,
)

admin.site.site_header = "TalentBridge AI Admin"
admin.site.site_title = "TalentBridge AI Admin"
admin.site.index_title = "Workspace overview"


@admin.register(JobAlertPreference)
class JobAlertPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "location", "enabled", "updated_at")
    list_filter = ("enabled", "job_type", "work_mode", "updated_at")
    search_fields = ("user__email", "title", "location", "skills")


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "job__title", "job__company__name")
    readonly_fields = ("user", "job", "preference", "matched_fields", "created_at")

    def has_add_permission(self, request):
        return False


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "industry", "location", "is_approved", "created_at")
    list_filter = ("is_approved", "industry")
    search_fields = ("name", "industry", "location", "owner__email")
    actions = ("approve_employers", "reject_employers")

    @admin.action(description="Approve selected employer accounts")
    def approve_employers(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} employer account(s) approved.", messages.SUCCESS)

    @admin.action(description="Return selected employer accounts to pending")
    def reject_employers(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"{count} employer account(s) set to pending.", messages.WARNING)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "job_type", "location", "is_active", "is_demo", "posted_at")
    list_filter = ("job_type", "is_active", "is_demo", "company__is_approved")
    search_fields = ("title", "company__name", "location", "skills")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "is_discoverable", "phone", "location", "experience")
    list_filter = ("role", "is_discoverable")
    search_fields = ("full_name", "user__email", "phone", "location", "skills")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "submitted_at")
    list_filter = ("status", "submitted_at")
    search_fields = ("job__title", "applicant__email", "applicant__profile__full_name")

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "topic", "received_at")
    list_filter = ("topic", "received_at")
    search_fields = ("name", "email", "message")



@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("user__email", "job__title", "job__company__name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__email", "title", "message")


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "scheduled_at", "status", "created_by")
    list_filter = ("status", "scheduled_at")
    search_fields = ("application__applicant__email", "application__job__title")


@admin.register(SignupRecord)
class SignupRecordAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "signup_method", "role", "email_verified", "created_at")
    list_filter = ("signup_method", "role", "email_verified", "created_at")
    search_fields = ("email", "user__username", "user__first_name", "user__last_name")
    readonly_fields = ("user", "email", "signup_method", "role", "email_verified", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
