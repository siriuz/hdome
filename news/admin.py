from django.contrib import admin
from news.models import *

class ArticleMediaInline(admin.TabularInline):
    model = Article.media.through

class ArticleInline(admin.TabularInline):
    model = Article.media.through

class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        ArticleMediaInline,
    ]
    exclude = ('media',)

class MediaAdmin(admin.ModelAdmin):
    inlines = [
        ArticleMediaInline,
    ]

# Register your models here.
admin.site.register(Article, ArticleAdmin)
admin.site.register(Media, MediaAdmin)
