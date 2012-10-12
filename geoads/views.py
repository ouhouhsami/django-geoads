#-*- coding: utf-8 -*-
"""
Views for ads application

This module provides CRUD absraction functions.

"""
import logging
from pygeocoder import Geocoder

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.gis.geos import Point
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import QueryDict, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.decorators import method_decorator
from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
    DeleteView, TemplateView, FormView)

from geoads.models import Ad, AdSearch, AdPicture, AdSearchResult
from geoads.forms import (AdContactForm, AdPictureForm, AdSearchForm,
    AdSearchUpdateForm, AdSearchResultContactForm, BaseAdForm)

logger = logging.getLogger(__name__)


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

    GET method for searching: filtering, ordering, and browsing by page results
    POST method for saving a search

    """
    model = Ad
    search_id = None
    template_name = 'geoads/search.html'
    context_object_name = 'filter'
    no_results_msg = None  # Message when there is no results
    results_msg = None  # Message when number of results > 0
    ad_search_form = None
    ad_search = None
    #BUG: paginate_by = 14 doesn't work, I use django-paginator

    def dispatch(self, request, *args, **kwargs):
        # here, dispatch according to the request.method and url args/kwargs

        if 'search_id' in kwargs:
            self.search_id = kwargs['search_id']

        self.request = request
        self.args = args
        self.kwargs = kwargs

        if request.method == 'POST':
            if self.search_id:
                logger.info('update_search')
                return self.update_search(request, *args, **kwargs)
            else:
                logger.info('create_search')
                return self.create_search(request, *args, **kwargs)
        else:
            if self.search_id:
                logger.info('read_search')
                return self.read_search(request, *args, **kwargs)
            elif request.GET != {}:
                logger.info('filter_search')
                return self.filter_ads(request, *args, **kwargs)
            else:
                logger.info('home')
                return self.home(request, *args, **kwargs)

        #return super(AdSearchView, self).dispatch(request, *args, **kwargs)

    def home(self, request, *args, **kwargs):
        # request.method == 'GET' and request.GET only contains pages and sorting
        self._q = None
        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list,
            initial_ads=True)
        return self.render_to_response(context)

    def filter_ads(self, request, *args, **kwargs):
        # request.method == 'GET' and request.GET != {} # after removing pages and potential sorting
        self._q = self.request.GET
        self.object_list = self.get_queryset()
        data = {'user': self.request.user,
            'search': self.request.GET.copy().urlencode()}
        self.ad_search_form = AdSearchForm(data)
        context = self.get_context_data(object_list=self.object_list,
            ad_search_form=True)
        self.get_msg()
        return self.render_to_response(context)

    def read_search(self, request, *args, **kwargs):
        # request.method == 'GET' and search_id is not None
        self.ad_search = AdSearch.objects.get(id=self.search_id)
        if self.ad_search.user != self.request.user:
                raise Http404
        self._q = QueryDict(self.ad_search.search)
        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list)
        self.get_msg()
        return self.render_to_response(context)

    @method_decorator(login_required)
    def create_search(self, request, *args, **kwargs):
        # request.method == 'POST' and search_id is None
        # save the search
        profile_detail_url = account_url(self.request)
        # return the results
        self.ad_search_form = AdSearchForm(request.POST)
        if self.ad_search_form.is_valid():
            logger.info('ad search form valid')
            self.ad_search_form.user = request.user
            self.ad_search = self.ad_search_form.save(commit=False)
            self.ad_search.content_type = ContentType.objects.get_for_model(self.model)
            self.ad_search.user = request.user
            self.ad_search.public = True
            self.ad_search.save()
            self.search_id = self.ad_search.id
            messages.add_message(self.request, messages.INFO,
                _(u'Votre recherche a bien été sauvegardée ' +
                u'dans <a href="%s">votre compte</a>.')
                % (profile_detail_url), fail_silently=True)
                # when creation, we need to save related ads to ad_search_results
            #self.update_ad_search_results()
            return HttpResponseRedirect(reverse('search',
                kwargs={'search_id': self.search_id}))
        # this would be better no ?
        #self._q = QueryDict(self.ad_search.search)
        #self.object_list = self._get_queryset()
        #context = self.get_context_data(object_list=self.object_list)
        #return self.render_to_response(context)

    @method_decorator(login_required)
    def update_search(self, request, *args, **kwargs):
        # request.method == 'POST' and search_id is not None
        profile_detail_url = account_url(self.request)
        self.ad_search = AdSearch.objects.get(id=self.search_id)
        self.ad_search_form = AdSearchForm(request.POST, instance=self.ad_search)
        if self.ad_search_form.is_valid():
            self.ad_search_form.save()
            messages.add_message(self.request, messages.INFO,
                _(u'Votre recherche a bien été mise à jour ' +
                  u'dans <a href="%s">votre compte</a>.')
                % (profile_detail_url), fail_silently=True)
        # need to be sure that self.ad_search.search is well updated
        self._q = QueryDict(self.ad_search.search)
        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list)
        self.get_msg()
        return self.render_to_response(context)

    def get_queryset(self):
        filter = self.model.filterset(self._q)
        return filter

    def get_context_data(self, initial_ads=None, ad_search_form=None, **kwargs):
        context = super(AdSearchView, self).get_context_data(**kwargs)
        if initial_ads == True:
            context['initial_ads'] = self.model.objects.select_related()\
                .order_by('-create_date')[0:10]
        if ad_search_form == True:
            context['ad_search_form'] = self.ad_search_form  # need to be filled with current search
        context['search_id'] = self.search_id  # what to do with that
        return context

    def get_msg(self):
        """
        Search result default message

        """
        if len(self.object_list.qs) == 0:
            messages.add_message(self.request, messages.INFO,
                self.get_no_results_msg(), fail_silently=True)
        else:
            messages.add_message(self.request, messages.INFO,
                self.get_results_msg(), fail_silently=True)

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
                    len(self.object_list.qs)) \
                            % (len(self.object_list.qs))
            return msg
        return self.results_msg


class AdSearchUpdateView(LoginRequiredMixin, UpdateView):
    """
    Class based update search view
    Render public or not
    Attach message

    """
    model = AdSearch
    form_class = AdSearchUpdateForm
    template_name = "geoads/adsearch_update.html"

    def get_success_url(self):
        return account_url(self.request)


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
            _(u'Votre recherche a bien été supprimée.'), fail_silently=True)
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

    @method_decorator(login_required)
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
                _(u'Votre message a bien été envoyé.'), fail_silently=True)
        return render_to_response(self.template_name, {'ad': self.get_object(),
                                  'contact_form': contact_form,
                                  'sent_mail': sent_mail},
                                  context_instance=RequestContext(request))

    def get_queryset(self):
        # below should return moderated objects w/ django-moderation
        # need latter expertise
        return self.model.objects.all()


class AdCreateView(LoginRequiredMixin, CreateView):
    """
    Class based create ad

    """
    model = Ad  # overriden in specific project urls
    template_name = 'geoads/edit.html'
    ad_picture_form = AdPictureForm

    def form_valid(self, form):
        logger.info('Form is valid, Ad creation')
        context = self.get_context_data()
        picture_formset = context['picture_formset']
        if picture_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            user_entered_address = form.cleaned_data['user_entered_address']
            if settings.BYPASS_GEOCODE == True:
                self.object.address = u"[{u'geometry': {u'location': {u'lat': 48.868356, u'lng': 2.330378}, u'viewport': {u'northeast': {u'lat': 48.8697049802915, u'lng': 2.331726980291502}, u'southwest': {u'lat': 48.8670070197085, u'lng': 2.329029019708498}}, u'location_type': u'ROOFTOP'}, u'address_components': [{u'long_name': u'1', u'types': [u'street_number'], u'short_name': u'1'}, {u'long_name': u'Rue de la Paix', u'types': [u'route'], u'short_name': u'Rue de la Paix'}, {u'long_name': u'2nd arrondissement of Paris', u'types': [u'sublocality', u'political'], u'short_name': u'2nd arrondissement of Paris'}, {u'long_name': u'Paris', u'types': [u'locality', u'political'], u'short_name': u'Paris'}, {u'long_name': u'Paris', u'types': [u'administrative_area_level_2', u'political'], u'short_name': u'75'}, {u'long_name': u'\xcele-de-France', u'types': [u'administrative_area_level_1', u'political'], u'short_name': u'IdF'}, {u'long_name': u'France', u'types': [u'country', u'political'], u'short_name': u'FR'}, {u'long_name': u'75002', u'types': [u'postal_code'], u'short_name': u'75002'}], u'formatted_address': u'1 Rue de la Paix, 75002 Paris, France', u'types': [u'street_address']}]"
                self.object.location = 'POINT (2.3303780000000001 48.8683559999999986)'
            else:
                geocode = Geocoder.geocode(user_entered_address.encode('ascii', 'ignore'))
                self.object.address = geocode.raw
                coordinates = geocode[0].coordinates
                pnt = Point(coordinates[1], coordinates[0], srid=900913)
                self.object.location = pnt
            self.object.save()
            picture_formset.instance = self.object
            picture_formset.save()
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
    form_class = BaseAdForm

    def form_valid(self, form):
        context = self.get_context_data()
        picture_formset = context['picture_formset']
        if picture_formset.is_valid():
            self.object = form.save(commit=False)
            user_entered_address = form.cleaned_data['user_entered_address']
            if settings.BYPASS_GEOCODE == True:
                self.object.address = u"[{u'geometry': {u'location': {u'lat': 48.868356, u'lng': 2.330378}, u'viewport': {u'northeast': {u'lat': 48.8697049802915, u'lng': 2.331726980291502}, u'southwest': {u'lat': 48.8670070197085, u'lng': 2.329029019708498}}, u'location_type': u'ROOFTOP'}, u'address_components': [{u'long_name': u'1', u'types': [u'street_number'], u'short_name': u'1'}, {u'long_name': u'Rue de la Paix', u'types': [u'route'], u'short_name': u'Rue de la Paix'}, {u'long_name': u'2nd arrondissement of Paris', u'types': [u'sublocality', u'political'], u'short_name': u'2nd arrondissement of Paris'}, {u'long_name': u'Paris', u'types': [u'locality', u'political'], u'short_name': u'Paris'}, {u'long_name': u'Paris', u'types': [u'administrative_area_level_2', u'political'], u'short_name': u'75'}, {u'long_name': u'\xcele-de-France', u'types': [u'administrative_area_level_1', u'political'], u'short_name': u'IdF'}, {u'long_name': u'France', u'types': [u'country', u'political'], u'short_name': u'FR'}, {u'long_name': u'75002', u'types': [u'postal_code'], u'short_name': u'75002'}], u'formatted_address': u'1 Rue de la Paix, 75002 Paris, France', u'types': [u'street_address']}]"
                self.object.location = 'POINT (2.3303780000000001 48.8683559999999986)'
            else:
                geocode = Geocoder.geocode(user_entered_address.encode('ascii', 'ignore'))
                self.object.address = geocode.raw
                coordinates = geocode[0].coordinates
                pnt = Point(coordinates[1], coordinates[0], srid=900913)
                self.object.location = pnt
            self.object.save()
            picture_formset.instance = self.object
            picture_formset.save()
            return redirect('complete', permanent=True)
        #TODO: if formset not valid

    #unused
    #def form_invalid(self, form):
    #    print 'KLKLKLKLK'
    #    return self.render_to_response(self.get_context_data(form=form))

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = self.model.objects.get(id=self.kwargs['pk'])
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

    def get_object(self, queryset=None):
        """ Ensure object is owned by request.user. """
        obj = super(AdDeleteView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        """ Redirect to user account page"""
        messages.add_message(self.request, messages.INFO,
            _(u'Votre annonce a bien été supprimée.'), fail_silently=True)
        return account_url(self.request)


class AdPotentialBuyersView(LoginRequiredMixin, ListView):
    """
    Class based view for listing potential buyers of an ad

    """
    model = Ad
    search_model = AdSearchResult
    template_name = "geoads/adpotentialbuyers_list.html"
    pk = None

    def get_queryset(self):
        # should return a list of buyers, in fact AdSearch instances
        self.pk = self.kwargs['pk']
        content_type = ContentType.objects.get_for_model(self.model)

        # Below an implementation that could be used to return form
        # AdSearchResultFormSet = modelformset_factory(AdSearchResult, form=AdSearchResultContactForm)
        # formset = AdSearchResultFormSet(queryset=AdSearchResult.objects.filter(object_pk=self.pk).filter(content_type=content_type))
        # return formset

        queryset = self.search_model.objects.filter(object_pk=self.pk)\
            .filter(content_type=content_type).filter(ad_search__public=True)
        for obj in queryset:
            obj.form = AdSearchResultContactForm(instance=obj)
            obj.form_action = reverse('contact_buyer', kwargs={'adsearchresult_id': obj.id})
        return queryset

    def get_context_data(self, **kwargs):
        """extra context"""
        context = super(AdPotentialBuyersView, self).get_context_data(**kwargs)
        context['object'] = self.model.objects.get(id=self.pk)
        return context


class AdPotentialBuyerContactView(LoginRequiredMixin, FormView):
    """
    Potential buyer contact view for an Ad

    """
    form_class = AdSearchResultContactForm

    def form_valid(self, form):
        self.message = form.cleaned_data['message']
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        self.adsearchresult_id = self.kwargs['adsearchresult_id']
        ad_search_result = AdSearchResult.objects.get(id=self.adsearchresult_id)
        ad_search_result.contacted = True
        ad_search_result.save()
        msg_from = ad_search_result.content_object.user.email
        msg_to = ad_search_result.ad_search.user.email
        send_mail('Contact', self.message, msg_from,
            [msg_to, ], fail_silently=False)
        return reverse('contact_buyers', kwargs={'pk': ad_search_result.object_pk})
