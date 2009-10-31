from django.conf.urls.defaults import *
from django.contrib.comments.urls import urlpatterns as contrib_comments_urlpatterns
from django.conf import settings

urlpatterns = patterns('mptt_comments.views',
    url(r'^new/(\d+)/$',
        'new_comment',
        name='new_comment'
    ),
    url(r'^reply/(\d+)/$',
        'new_comment',
        name='comment_reply'
    ),
    url(r'^post/$',
        'post_comment',
        name='comments_post_comment'
    ),
    url(r'^posted-ajax/$',
        'comment_done_ajax',
        name='comments_comment_done_ajax'
    ),
    url(r'^more/(\d+)/$',
        'comments_more',
        name='comments_more'
    ),
    url(r'^replies/(\d+)/$',
        'comments_subtree',
        name='comments_subtree'
    ),
    url(r'^detail/(\d+)/$',
        'comments_subtree',
        name='comment_detail',
        kwargs={'include_self': True, 'include_ancestors': True}
    )
    
)

urlpatterns += contrib_comments_urlpatterns
