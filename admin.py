from django.contrib import admin

from .models import Council, Project, Category, News, Community, Supplier
from .models import CouncilMeeting, Event


class CouncilAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "contact", "contact_email", "created_at")
    search_fields = ("name", "contact", "contact_email")
    list_filter = ("created_at",)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "council", "category", "budget", "created_at")
    search_fields = ("title", "description", "council__name")
    list_filter = ("council", "category", "created_at")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title", "summary")
    list_filter = ("created_at",)


class CommunityAdmin(admin.ModelAdmin):
    list_display = ("title", "link")
    search_fields = ("title",)


admin.site.register(Council, CouncilAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Supplier)

class CouncilMeetingAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'location', 'council', 'archived')
    list_filter = ('date', 'council', 'archived')
    search_fields = ('location', 'agenda')


admin.site.register(CouncilMeeting, CouncilMeetingAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'council', 'project')
    list_filter = ('date', 'council')
    search_fields = ('title', 'description', 'location')

    readonly_fields = ('preview',)
    fieldsets = (
        (None, {'fields': ('title', 'description', 'date', 'time', 'location', 'council', 'project')}),
        ('Images', {'fields': ('image', 'image_file', 'preview')}),
    )

    def preview(self, obj):
        if not obj:
            return ''
        url = obj.image_file.url if obj.image_file else obj.image
        if url:
            return f"<img src='{url}' style='max-width:320px; height:auto; border-radius:6px'/>"
        return ''
    preview.allow_tags = True
    preview.short_description = 'Preview'


admin.site.register(Event, EventAdmin)




