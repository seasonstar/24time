from django.db import models
from django.contrib import admin
from django.forms import ModelForm

class Post(models.Model):
    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

class PostAdmin(admin.ModelAdmin):
    search_fields = ['title']

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=60)
    body = models.TextField()
    post = models.ForeignKey(Post)

    def __unicode__(self):
        return u'%s: %s' % (self.post,self.body[:10])

class CommentAdmin(admin.ModelAdmin):
    display_fields = ['post', 'author' ,'created']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ['post']

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
