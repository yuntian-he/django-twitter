from django.contrib import admin


# Register your models here.
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('created_at',
                    'user',
                    'content',
                    )