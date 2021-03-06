from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.shortcuts import render
from django.contrib.auth.models import User
from django import forms
from django.http import *
from django.core.urlresolvers import reverse
import django_tables2 as tables
from django_tables2.utils import A
from base.views import render_with_layout
from base.utils import *
from .models import *

from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class ForumTable(tables.Table):
  class Meta:
    orderable = False
    attrs = {
      "class" : 'table table-striped table-hover table-condensed'
    }

class ForumMostRecentTable(ForumTable):
  titel = tables.LinkColumn('forum.draad', args=[A('draad_id')])
  laatst_gewijzigd = tables.DateTimeColumn(orderable=True)

  class Meta(ForumTable.Meta):
    model = ForumDraad
    fields = ('uid_id', 'titel', 'laatst_gewijzigd', 'laatste_wijziging_uid_id')
    order_by = ('-laatst_gewijzigd',)

class ForumPostForm(forms.ModelForm):
  class Meta:
    model = ForumPost
    fields = ['draad', 'tekst']
    widgets = {
      'draad': forms.HiddenInput()
    }

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)

  def save(self, commit=True):
    post = super().save(commit=False)

    post.user = Profiel.objects.get(user=self.user)
    post.datum_tijd = datetime.now() #TODO
    post.laatst_gewijzigd = datetime.now()
    post.verwijderd = False
    post.auteur_ip = "" # TODO
    post.wacht_goedkeuring = -1 #TODO

    post.draad.laatst_gewijzigd = datetime.now()

    if commit:
      post.save()
      post.draad.save()

    return post

def forum_root(request):
  # find the forumdelen that may be seen by the user
  delen = list(ForumDeel.get_viewable_by(request.user))
  queryset = ForumDraad.objects.filter(forum__in=delen)

  # filter on forum deel
  if 'forum' in request.GET:
    titel = ForumDeel.objects.get(pk=request.GET['forum']).titel + " Reformaforum"
    queryset = queryset.filter(forum_id=request.GET['forum'])
  else:
    titel = "Reformaforum"

  table = ForumMostRecentTable(queryset)
  table.paginate(page=request.GET.get('page', 1), per_page=25)

  cats = grouped_dict(map(lambda d: (d.categorie, d), delen))

  return render_with_layout(request, 'forum_main.html', title=titel, ctx={
    'categories': cats,
    'posts': table
  })

def forum_draad(request, draad_id):
  draad = ForumDraad.objects.prefetch_related('forum').get(pk=draad_id)
  fresh_form = ForumPostForm(initial={'draad': draad})

  # make sure the user can view the forum draad
  deny_on_fail(request.user.has_perm('forum.view_forumdeel', draad.forum))
  can_post = request.user.has_perm('forum.post_in_forumdeel', draad.forum)

  if request.method == 'POST':
    # if the user is posting, make sure he has the permissions to post here
    deny_on_fail(can_post)

    # initiate the filled in form
    form = ForumPostForm(request.POST, user=request.user)

    if form.is_valid():
      form.save()

      # use a fresh form for the next page
      return HttpResponseRedirect(reverse('forum.draad', args=[draad_id]))
  else:
    form = fresh_form

  posts = ForumPost.objects.all()\
    .filter(draad_id=draad_id)\
    .order_by('datum_tijd')

  return render_with_layout(request, 'forum_draad.html', title="Forum draad %s" % draad.titel, ctx={
    'draad': draad,
    'posts': posts,
    'new_post_form': form,
    'can_post': can_post
  })

urls = patterns('',
   url(r'^$', forum_root, name='forum.main'),
   url(r'^(\d+)/$', forum_draad, name='forum.draad')
)
