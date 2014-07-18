from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    author = models.ForeignKey( User )
    title = models.CharField( max_length = 400 )
    content = models.TextField( )
    created = models.DateTimeField( )
    media = models.ManyToManyField( 'Media', blank=True, null=True )

    def __str__(self):
        return self.title + '|' + self.author.username

class Media(models.Model):
    photo = models.FileField( blank=True, null=True)
    url = models.URLField( blank=True, null=True)

    def __str__(self):
        if self.photo and self.url:
            return self.url + '|' + self.photo.url
        elif self.photo:
            return '<blank>|' + self.photo.url
        elif self.url:
            return self.url + '|<blank>'
        else:
            return '<blank>|<blank>'

# Create your models here.
