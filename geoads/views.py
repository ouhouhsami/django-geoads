# coding=utf-8
"""
Views for ads application

This module provides CRUD absraction functions.
"""

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.http import QueryDict, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView


from geoads.models import Ad, AdSearch, AdPicture, AdSearchResult
from geoads.forms import AdContactForm, AdPictureForm, AdSearchForm


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


def account_url(request):
    try:
        url = settings.ADS_PROFILE_URL % (request.user.username)
    except:
        url = settings.ADS_PROFILE_URL
    return url


class AdSearchView(ListView):
    """
    Class based ad search view

    Not really clean yet, get-post condition in the above get_queryset functions

    GET method for searching: filtering, ordering, and browsing by page results
    POST method for saving

    """

    model = Ad
    filterset_class = None
    search_id = None
    template_name = 'geoads/search.html'
    context_object_name = 'filter'
    no_results_msg = None  # Message when there is no results
    results_msg = None  # Message when nb_of_results > 0
    nb_of_results = None  # Number of results for a search
    search_query = None  # hold the search as in the URL, used to save/update AdSearch via AdSearchForm
    #BUG: paginate_by = 14 doesn't work, i use django-paginator
    state = None  # 5 states: None, search, create_search, update_search, read_search
    ad_search_form = None
    ad_search = None

    def get_queryset(self):
        # this function should only do a get_queryset,
        # no form save creation/update

        # test if request is for a saved search
        if self.state is None:  # no create_search or update_search (no POST)
            if 'search_id' in self.kwargs:
                self.state = 'read_search'
                self.search_id = self.kwargs['search_id']
                self.ad_search = AdSearch.objects.get(id=self.search_id)
                if self.ad_search.user != self.request.user:
                    raise Http404
                q = QueryDict(self.ad_search.search)  # this should be modified if self.request.GET != {} no ?, to upd old search
                filter = self.filterset_class(q or None, search=True)
                self.ad_search_form = AdSearchForm(instance=self.ad_search)  # upd with current self.request.GET ?
            elif self.request.GET != {}:  # TODO: need to remove sort or page params
                self.state = 'search'
                filter = self.filterset_class(self.request.GET, search=True)
                datas = self.request.GET.copy()
                #del datas['save_and_search']
                #del datas['csrfmiddlewaretoken']
                data = {'user': self.request.user, 'search': datas.urlencode()}
                self.ad_search_form = AdSearchForm(data)  # set auto_id=True ? I don't think so
            else:
                # default case: no query, no saved search
                filter = self.filterset_class(None, search=False)

        else:  # here we come from POST, we are in create_search or update_search state
            # coming from POST: we have saved if needed, we have created or updated search
            # we can get value from it
            q = QueryDict(self.ad_search.search)
            filter = self.filterset_class(q or None, search=True)
            # here we save search AdSearchResult instances
            print 'save instance'
            for ad in filter.qs:
                print ad
                ad_search_result, created = AdSearchResult.objects.get_or_create(
                    ad_search=self.ad_search,
                    content_type=self.ad_search.content_type,
                    object_pk=ad.id)
                print ad_search_result, created
            if self.state == 'create_search':
                # for self.state = 'create_search', redirect to url with search_id, so that update will be possible
                # this is here to be sure that we have created the ad search results
                return HttpResponseRedirect(reverse('search', kwargs={'search_id': self.search_id}))

        if self.state is not None:
            # Search result message
            self.nb_of_results = len(filter.qs)  # len method is faster than count() in this case !
            if self.nb_of_results == 0:
                messages.add_message(self.request, messages.INFO, self.get_no_results_msg())
            if self.nb_of_results >= 1:
                messages.add_message(self.request, messages.INFO, self.get_results_msg())

        return filter

    @method_decorator(login_required)  # Check if user.is_authenticated just for post
    def post(self, request, *args, **kwargs):
        # POST, create or update search
        # removing the method decorator
        # we could save search for anonymous user ?

        profile_detail_url = account_url(self.request)

        if 'search_id' in self.kwargs:
            self.state = 'update_search'
            self.search_id = self.kwargs['search_id']
            self.ad_search = AdSearch.objects.get(id=self.search_id)
            self.ad_search_form = AdSearchForm(request.POST, instance=self.ad_search)
            if self.ad_search_form.is_valid():
                self.ad_search_form.save()
                messages.add_message(self.request, messages.INFO,
                _(u'Votre recherche a bien été mise à jour ' +
                  u'dans <a href="%s">votre compte</a>.')
                % (profile_detail_url))
        else:
            self.state = 'create_search'
            self.ad_search_form = AdSearchForm(request.POST)
            if self.ad_search_form.is_valid():
                self.ad_search_form.user = request.user
                self.ad_search = self.ad_search_form.save(commit=False)
                self.ad_search.content_type = ContentType.objects.get_for_model(self.model)
                self.ad_search.user = request.user
                self.ad_search.save()
                self.search_id = self.ad_search.id
                messages.add_message(self.request, messages.INFO,
                _(u'Votre recherche a bien été sauvegardée ' +
                  u'dans <a href="%s">votre compte</a>.')
                % (profile_detail_url))

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdSearchView, self).get_context_data(**kwargs)
        if self.request.method != 'POST' and self.request.GET == {} and self.search_id is None:
            context['search'] = False
            context['initial_ads'] = self.model.objects.select_related()\
                            .filter(delete_date__isnull=True)\
                            .order_by('-create_date')[0:10]
        else:
            context['search'] = True
        # if recall save search
        # also, coming from POST we shoudn't propose save search
        # so we set ad_search_form to None
        if self.state == 'create_search' or self.state == 'update_search':
            self.ad_search_form = None
        if self.state == 'read_search' and len(self.request.GET) == 0:
            self.ad_search_form = None
        context['ad_search_form'] = self.ad_search_form
        # this allow us to do {% url search search.id %} or {% ur search %} in template
        # in order to update or create search etc.
        context['search_id'] = self.search_id
        return context

    def get_no_results_msg(self):
        """
        Message for search that give 0 results
        """
        if self.no_results_msg is None:
            return _(u'Aucune annonce ne correspond à votre recherche. ' +\
                     u'Elargissez votre zone de recherche ou modifiez les critères.')
        return self.no_results_msg

    def get_results_msg(self):
        """
        Message for search that give 1 or more results
        """
        #TODO: should have information if search come from a saved search
        if self.results_msg is None:
            msg = ungettext(u'%s annonce correspondant à votre recherche. ',
                    u'%s annonces correspondant à votre recherche. ',
                    self.nb_of_results) \
                            % (self.nb_of_results)
            #if not self.request.user.is_authenticated():
            #    sign_url = settings.ADS_PROFILE_SIGNUP
            #    msg = msg + _(u'<a href="%s">Inscrivez-vous</a> pour recevoir' +
            #               u' les alertes mail ou enregistrer votre recherche.') % (sign_url)
            return msg
        return self.results_msg


class AdSearchDeleteView(LoginRequiredMixin, DeleteView):
    """
    Class based delete search ad
    """
    model = AdSearch
    template_name = "geoads/adsearch_confirm_delete.html"

    def get_object(self, queryset=None):
        """ Ensure object is owned by request.user. """
        obj = super(AdSearchDeleteView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        """ Redirect to user account page"""
        messages.add_message(self.request, messages.INFO,
                             _(u'Votre recherche a bien été supprimée.'))
        return account_url(self.request)


class AdDetailView(DetailView):
    """
    Class based detail ad
    """
    model = Ad  # changed in urls
    context_object_name = 'ad'
    template_name = 'geoads/view.html'

    def get_context_data(self, **kwargs):
        context = super(AdDetailView, self).get_context_data(**kwargs)
        context['contact_form'] = AdContactForm()
        context['sent_mail'] = False
        return context

    def post(self, request, *args, **kwargs):
        """ used for contact message between users """
        contact_form = AdContactForm(request.POST)
        sent_mail = False
        if contact_form.is_valid():
            instance = contact_form.save(commit=False)
            instance.content_object = self.get_object()
            instance.user = request.user
            instance.save()
            send_mail(_(u'[%s] Demande d\'information concernant votre annonce') \
            % (Site.objects.get_current().name),
               instance.message,
               instance.user.email,
               [self.get_object().user.email],
               fail_silently=False)
            sent_mail = True
            messages.add_message(request, messages.INFO,
                                 _(u'Votre message a bien été envoyé.'))
        return render_to_response(self.template_name, {'ad': self.get_object(),
                                  'contact_form': contact_form,
                                  'sent_mail': sent_mail},
                                  context_instance=RequestContext(request))

    def get_queryset(self):
        # below should return moderated objects w/ django-moderation
        return self.model.objects.all()


class AdCreateView(LoginRequiredMixin, CreateView):
    """
    Class based create ad
    """
    model = Ad  # overriden in specific project urls
    template_name = 'geoads/edit.html'
    ad_picture_form = AdPictureForm

    def form_valid(self, form):
        context = self.get_context_data()
        picture_formset = context['picture_formset']
        if picture_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.location = form.cleaned_data['location']
            self.object.address = form.cleaned_data['address']
            self.object.save()
            picture_formset.instance = self.object
            picture_formset.save()
            #TODO: why must we set this after having saved it a first time
            self.object.moderated_object.changed_by = self.request.user
            self.object.moderated_object.save()
            message = render_to_string('geoads/emails/ad_create_email_message.txt')
            subject = render_to_string('geoads/emails/ad_create_email_subject.txt',
                                  {'site_name': Site.objects.get_current().name})
            send_mail(subject, message, 'contact@achetersanscom.com',
                      [self.object.user.email], fail_silently=True)
            #return HttpResponseRedirect('complete/')
            return redirect('complete', permanent=True)
        #TODO: if formset not valid

    def form_invalid(self, form):
        send_mail(_(u"[%s] %s invalid form while creating an ad") %
                  (Site.objects.get_current().name, self.request.user.email),
                  "%s" % (form.errors), 'contact@achetersanscom.com',
                  ["contact@achetersanscom.com"], fail_silently=True)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(AdCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            PictureFormset = generic_inlineformset_factory(AdPicture, form=self.ad_picture_form,
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset(self.request.POST,
                                                        self.request.FILES)
        else:
            PictureFormset = generic_inlineformset_factory(AdPicture, form=self.ad_picture_form,
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset()
        return context


class AdUpdateView(LoginRequiredMixin, UpdateView):
    """
    Class base update ad
    """
    model = Ad  # overriden in specific project urls
    template_name = 'geoads/edit.html'
    ad_picture_form = AdPictureForm

    def form_valid(self, form):
        context = self.get_context_data()
        picture_formset = context['picture_formset']
        if picture_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.location = form.cleaned_data['location']
            self.object.address = form.cleaned_data['address']
            self.object.save()
            picture_formset.instance = self.object
            picture_formset.save()
            message = render_to_string(
                              'geoads/emails/ad_update_email_message.txt', {})
            subject = render_to_string(
                              'geoads/emails/ad_update_email_subject.txt',
                             {'site_name': Site.objects.get_current().name})
            send_mail(subject, message, 'contact@achetersanscom.com',
                          [self.object.user.email],
                          fail_silently=True)
            return redirect('complete', permanent=True)
        #TODO: if formset not valid

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = self.model.unmoderated_objects.get(id=self.kwargs['pk'])
        if not obj.user == self.request.user:
            raise Http404
        # TODO: ugly hack don't understand, if not line below, value is converted
        obj.location = str(obj.location)
        return obj

    def get_context_data(self, **kwargs):
        context = super(AdUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            PictureFormset = generic_inlineformset_factory(AdPicture, form=self.ad_picture_form,
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset(self.request.POST,
                                                  self.request.FILES,
                                                  instance=context['object'])
        else:
            PictureFormset = generic_inlineformset_factory(AdPicture, form=self.ad_picture_form,
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset(instance=context['object'])
        return context


class CompleteView(LoginRequiredMixin, TemplateView):
    template_name = "geoads/validation.html"


class AdDeleteView(LoginRequiredMixin, DeleteView):
    """
    Class based delete ad
    """
    model = Ad  # "normally" overrided in specific project urls
    template_name = "geoads/ad_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete_date = datetime.now()
        self.object.save()
        serialized_obj = serializers.serialize('json', [self.object, ])
        default_storage.save('deleted/%s-%s.json' % (self.object.id,
                                                    self.object.slug),
                                    ContentFile(serialized_obj))
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_queryset(self):
        return self.model.unmoderated_objects.all()

    def get_object(self, queryset=None):
        """ Ensure object is owned by request.user. """
        obj = super(AdDeleteView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        """ Redirect to user account page"""
        messages.add_message(self.request, messages.INFO,
                             _(u'Votre annonce a bien été supprimée.'))
        return account_url(self.request)
