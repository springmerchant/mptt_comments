from django.utils.encoding import force_unicode
from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.utils.translation import ungettext, ugettext_lazy as _

import time
import datetime

from mptt_comments.models import MpttComment

class MpttCommentForm(CommentForm):
    title = forms.CharField(max_length=255, label=_('Title'))
    parent_pk = forms.IntegerField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, target_object, parent_comment=None, data=None, initial=None):
        self.parent_comment = parent_comment
        super(MpttCommentForm, self).__init__(target_object, data=data, initial=initial)
        
        self.fields.keyOrder = [
            'title',
            'comment',
            'honeypot',
            'content_type',
            'object_pk',
            'timestamp',
            'security_hash',
            'parent_pk'
        ]
    
    def get_comment_object(self):
        """
        Return a new (unsaved) comment object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError("get_comment_object may only be called on valid forms")

        parent_comment = None
        parent_pk = self.cleaned_data.get("parent_pk")
        if parent_pk:
            parent_comment = MpttComment.objects.get(pk=parent_pk)
            
        new = MpttComment(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_unicode(self.target_object._get_pk_val()),
            user_name    = self.cleaned_data.get("name", ''),
            user_email   = self.cleaned_data.get("email", ''),
            user_url     = self.cleaned_data.get("url", ''),
            comment      = self.cleaned_data["comment"],
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False,
            title = self.cleaned_data["title"],
            parent = parent_comment
        )

        # Check that this comment isn't duplicate. (Sometimes people post comments
        # twice by mistake.) If it is, fail silently by returning the old comment.
        possible_duplicates = MpttComment.objects.filter(
            content_type = new.content_type,
            object_pk = new.object_pk,
            user_name = new.user_name,
            user_email = new.user_email,
            user_url = new.user_url,
            parent = parent_comment
        )
        for old in possible_duplicates:
            if old.submit_date.date() == new.submit_date.date() and old.comment == new.comment:
                return old

        return new
        
    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        security_dict =   {
            'content_type'  : str(self.target_object._meta),
            'object_pk'     : str(self.target_object._get_pk_val()),
            'timestamp'     : str(timestamp),
            'security_hash' : self.initial_security_hash(timestamp),
            'parent_pk'     : self.parent_comment and str(self.parent_comment.pk) or '',
            'title'         : self.parent_comment.level == 0 and force_unicode(self.target_object) or
                                u'%s%s' % ( (self.parent_comment.title[:3] != u'Re:') and 'Re: '  or u'', self.parent_comment.title)
        }
        
        return security_dict
