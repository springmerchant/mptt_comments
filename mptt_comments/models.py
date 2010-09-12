import mptt

from django.db import models
from django.contrib.comments.models import Comment

from mptt_comments.managers import MpttCommentManager

class MpttComment(Comment):
    title = models.CharField(max_length=255)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True)
    
    class Meta:
        ordering = ('tree_id', 'lft')
    
    objects = MpttCommentManager()

mptt.register(MpttComment)
