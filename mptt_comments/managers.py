import datetime

from django.contrib.comments.managers import CommentManager
from django.conf import settings

class MpttCommentManager(CommentManager):
    
    def get_root_comment(self, ctype, object_pk):
        root_comment, uorc = self.model.objects.get_or_create(
            parent=None,
            content_type=ctype,
            object_pk=object_pk,
            defaults={
                'comment': 'Root comment placeholder',
                'user_name': 'Noname',
                'user_email': 'no@user.no',
                'user_url': '',
                'submit_date': datetime.datetime.now(),
                'site_id': settings.SITE_ID
            })
            
        return root_comment
    
    def published(self):
        """retrieve comments published not removed"""
        return self.get_query_set().filter(is_removed=False, is_public=True, level__gt=0).order_by('-submit_date')
