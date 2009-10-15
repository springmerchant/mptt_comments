import re

from django.contrib.comments.templatetags.comments import BaseCommentNode, CommentListNode
from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.core import urlresolvers
from django.utils.safestring import mark_safe

from mptt_comments.models import MpttComment
from mptt_comments.forms import MpttCommentForm

register = template.Library()

class BaseMpttCommentNode(BaseCommentNode):
    
    root_node = None
    
    def __init__(self, ctype=None, object_pk_expr=None, object_expr=None, as_varname=None, comment=None):
        super(BaseMpttCommentNode, self). __init__(ctype=ctype, object_pk_expr=object_pk_expr, object_expr=object_expr, as_varname=as_varname, comment=comment)
        self.comment_model = MpttComment
    
    def get_root_node(self, context):
        if not self.root_node:
            ctype, object_pk = self.get_target_ctype_pk(context)
            self.root_node = self.comment_model.objects.get_root_comment(ctype, object_pk)
        return self.root_node
objects = {}

class MpttCommentFormNode(BaseMpttCommentNode):
   
    global objects
   
    """Insert a form for the comment model into the context."""
           
    def get_form(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
       
        key = str(ctype)+'_'+str(object_pk)
       
        if objects.has_key(key):
            return MpttCommentForm(objects[key], parent_comment=self.get_root_node(context))
        elif object_pk:
            objects[key] = ctype.get_object_for_this_type(pk=object_pk)
            return MpttCommentForm(objects[key], parent_comment=self.get_root_node(context))
        else:
            return None        

    def render(self, context):
        context[self.as_varname] = self.get_form(context)
        return ''

class MpttCommentListNode(BaseMpttCommentNode):

    offset = getattr(settings, 'MPTT_COMMENTS_OFFSET', 20)
    
    cutoff_level = getattr(settings, 'MPTT_COMMENTS_CUTOFF', 3)
    bottom_level = 0 
    
    def get_query_set(self, context):

        related = getattr(settings, 'MPTT_COMMENTS_SELECT_RELATED', None)

        qs = super(MpttCommentListNode, self).get_query_set(context)
        root_node = self.get_root_node(context)
        qs = qs.filter(tree_id=root_node.tree_id, level__gte=1, level__lte=self.cutoff_level).order_by('tree_id', 'lft')

        if related:
            qs = qs.select_related(*related)

        return qs
        
    def get_context_value_from_queryset(self, context, qs):
        return list(qs[:self.offset])
        
    def render(self, context):
        qs = self.get_query_set(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        comments_remaining = self.get_query_set(context).count()
        context['comments_remaining'] = (comments_remaining - self.offset) > 0 and comments_remaining - self.offset or 0
        context['root_comment'] = self.get_root_node(context)
        context['collapse_levels_above'] = 2
        context['cutoff_level'] = self.cutoff_level
        context['bottom_level'] = self.bottom_level
        return ''        

class MpttCommentCountNode(BaseMpttCommentNode):
    """Insert a count of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return qs.filter(level__gt=0).count()

def get_mptt_comment_count(parser, token):
    """
    Gets the comment count for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_mptt_comment_count for [object] as [varname]  %}
        {% get_mptt_comment_count for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_mptt_comment_count for event as comment_count %}
        {% get_mptt_comment_count for calendar.event event.id as comment_count %}
        {% get_mptt_comment_count for calendar.event 17 as comment_count %}

    """
    return MpttCommentCountNode.handle_token(parser, token)

def get_mptt_comment_list(parser, token):
    """
    Gets the list of comments for the given params and populates the template
    context with a variable containing that value, whose name is defined by the
    'as' clause.

    Syntax::

        {% get_comment_list for [object] as [varname]  %}
        {% get_comment_list for [app].[model] [object_id] as [varname]  %}

    Example usage::

        {% get_comment_list for event as comment_list %}
        {% for comment in comment_list %}
            ...
        {% endfor %}

    """
    return MpttCommentListNode.handle_token(parser, token)


def get_mptt_comment_form(parser, token):
    """
    Get a (new) form object to post a new comment.

    Syntax::

        {% get_comment_form for [object] as [varname] %}
        {% get_comment_form for [app].[model] [object_id] as [varname] %}
    """
    return MpttCommentFormNode.handle_token(parser, token)


def mptt_comment_form_target():
    """
    Get the target URL for the comment form.

    Example::

        <form action="{% comment_form_target %}" method="POST">
    """
    return urlresolvers.reverse("mptt_comments.views.post_comment")

def children_count(comment):
    return (comment.rght - comment.lft) / 2

def mptt_comments_media():

    return mark_safe( render_to_string( ('comments/comments_media.html',) , { }) )
    
def display_comment_toplevel_for(target):

    model = target.__class__
        
    template_list = [
        "comments/%s_%s_display_comments_toplevel.html" % tuple(str(model._meta).split(".")),
        "comments/%s_display_comments_toplevel.html" % model._meta.app_label,
        "comments/display_comments_toplevel.html"
    ]
    return render_to_string(
        template_list, {
            "object" : target
        } 
        # RequestContext(context['request'], {})
    )

class LatestMpttComments(template.Node):
    def __init__(self, limit, var_name):
        self.limit = limit
        self.var_name = var_name

    def render(self, context):
        comments = MpttComment.objects.published()[:int(self.limit)]
        if comments and (int(self.limit) == 1):
            context[self.var_name] = comments[0]
        else:
            context[self.var_name] = comments
        return ''

def get_latest_comments(parser, token):
    """
    Gets any number of latest comments and stores them in a varable.

    Syntax::

        {% get_latest_comments [limit] as [var_name] %}

    Example usage::

        {% get_latest_comments 10 as latest_comment_list %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    format_string, var_name = m.groups()
    return LatestMpttComments(format_string, var_name)
    
register.filter(children_count)
register.tag(get_mptt_comment_form)
register.simple_tag(mptt_comment_form_target)
register.simple_tag(mptt_comments_media)
register.tag(get_mptt_comment_list)
register.tag(get_latest_comments)
register.tag(get_mptt_comment_count)
register.simple_tag(display_comment_toplevel_for)
