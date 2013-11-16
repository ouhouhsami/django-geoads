#-*- coding: utf-8 -*-
"""
Views for ads application

This module provides class-based views Create/Read/Update/Delete absractions
to work with Ad models.
"""
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import QueryDict, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.decorators import method_decorator
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, View,
                                  DeleteView, TemplateView, FormView)
from django.views.generic.detail import SingleObjectMixin

from django_filters.views import FilterView

from geoads.models import Ad, AdSearch, AdPicture, AdSearchResult

from geoads.forms import (AdContactForm, AdPictureForm, AdSearchForm,
                          AdSearchUpdateForm, AdSearchResultContactForm, BaseAdForm)
from geoads.utils import geocode
from geoads.signals import geoad_vendor_message, geoad_user_message


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class DefaultAdListView(FilterView):
    template_name = 'geoads/search.html'


class AdListView(FilterView):
    model = Ad
    
    def get(self, request, *args, **kwargs):
        # Used to reach the home page 
        # or view a specific search
        # This search can come from a saved search
        # or just filtering of ads
        if 'search_id' in self.request.GET:
            ad_search = AdSearch.objects.get(id=self.request.GET['search_id'])
            if ad_search.user != request.user:
                return HttpResponseForbidden()
            params = QueryDict(ad_search.search).urlencode()
            self.request.session['ad_search'] = ad_search
            return HttpResponseRedirect(request.path+"?%s" % params)
        view = DefaultAdListView.as_view(model=self.model, filterset_class = self.model.filterset())
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Only for creating a search
        # or updating an existing one
        # We store it in session: self.request.session['search_id']
        q = request.GET.copy()
        [q.pop(elt[0]) for elt in q.lists() if elt[1] == [u'']]
        search = q.urlencode()
        if 'ad_search' not in request.session:
            # Create a search
            ad_search = AdSearch(user=request.user, search=search, public=True)
            ad_search.content_type = ContentType.objects.get_for_model(self.model)
            ad_search.save()
        else:
            # or just update it
            ad_search = self.request.session['ad_search']
            if ad_search.user != request.user:
                return HttpResponseForbidden()
            ad_search.search = search
            ad_search.save()
        return HttpResponseRedirect(request.path+"?search_id=%s" % ad_search.id)

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
        # Dispatch according to the request.method and url args/kwargs

        if 'search_id' in kwargs:
            self.search_id = kwargs['search_id']

        self.request = request
        self.args = args
        self.kwargs = kwargs

        if request.method == 'POST':
            if self.search_id:
                return self.update_search(request, *args, **kwargs)
            else:
                return self.create_search(request, *args, **kwargs)
        else:
            if self.search_id:
                return self.read_search(request, *args, **kwargs)
            elif request.GET != {}:
                return self.filter_ads(request, *args, **kwargs)
            else:
                return self.home(request, *args, **kwargs)

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
        self.ad_search_form = AdSearchForm(request.POST)
        if self.ad_search_form.is_valid():
            self.ad_search_form.user = request.user
            self.ad_search = self.ad_search_form.save(commit=False)
            self.ad_search.content_type = ContentType.objects.get_for_model(self.model)
            self.ad_search.user = request.user
            self.ad_search.public = True
            self.ad_search.save()
            self.search_id = self.ad_search.id
            messages.add_message(self.request, messages.INFO,
                _(u'Votre recherche a bien été sauvegardée dans votre compte</a>.'), fail_silently=True)
            return HttpResponseRedirect(reverse('search',
                kwargs={'search_id': self.search_id}))

    @method_decorator(login_required)
    def update_search(self, request, *args, **kwargs):
        # request.method == 'POST' and search_id is not None
        profile_detail_url = settings.LOGIN_REDIRECT_URL
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
        filter = self.model.filterset()(self._q)
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
    success_url = settings.LOGIN_REDIRECT_URL


class AdSearchDeleteView(DeleteView):
    """
    Class based delete search ad
    """
    model = AdSearch
    template_name = "geoads/adsearch_confirm_delete.html"
    success_url = settings.LOGIN_REDIRECT_URL


    def get_object(self, queryset=None):
        """ Ensure object is owned by request.user. """
        obj = super(AdSearchDeleteView, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj


class AdDisplay(DetailView):
    context_object_name = 'ad'
    template_name = 'geoads/view.html'
    contact_form = AdContactForm    

    def get_context_data(self, **kwargs):
        context = super(AdDisplay, self).get_context_data(**kwargs)
        context['contact_form'] = self.contact_form()
        if 'sent_mail' in self.request.session and self.get_object() in self.request.session['sent_mail']: 
            context['sent_mail'] = True
        else:
            context['sent_mail'] = False
        return context


class AdMessage(SingleObjectMixin, FormView):
    template_name = 'geoads/view.html'

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()
        self.object = self.get_object()
        self.request = request
        return super(AdMessage, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        geoad_user_message.send(sender=Ad, ad=self.object, user=self.request.user, message=form.cleaned_data['message'])
        messages.add_message(self.request, messages.INFO,
                _(u'Votre message a bien été envoyé.'), fail_silently=True)

        # Use session to store already sent mails
        if not 'sent_mail' in self.request.session or not self.request.session['sent_mail']:
            self.request.session['sent_mail'] = [self.object]
        else:
            sent_mail_list = self.request.session['sent_mail']
            sent_mail_list.append(self.object)
            self.request.session['sent_mail'] = sent_mail_list

        return super(AdMessage, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class AdDetailView(View):
    """
    Class based detail ad
    """
    model = Ad  # changed in urls
    contact_form = AdContactForm     
    def get(self, request, *args, **kwargs):
        view = AdDisplay.as_view(model=self.model, contact_form=self.contact_form)
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = AdMessage.as_view(model=self.model, form_class=self.contact_form)
        return view(request, *args, **kwargs)


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
            user_entered_address = form.cleaned_data['user_entered_address']
            geo_info = geocode(user_entered_address.encode('ascii', 'ignore'))
            self.object.address = geo_info['address']
            self.object.location = geo_info['location']
            self.object.save()
            picture_formset.instance = self.object
            picture_formset.save()
            return redirect('complete', permanent=True)

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
            geo_info = geocode(user_entered_address.encode('ascii', 'ignore'))
            self.object.address = geo_info['address']
            self.object.location = geo_info['location']
            self.object.save()
            picture_formset.instance = self.object
            picture_formset.save()
            return redirect('complete', permanent=True)


    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = self.model.objects.get(id=self.kwargs['pk'])
        if not obj.user == self.request.user:
            raise Http404

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
        messages.add_message(self.request, messages.INFO, _(u'Votre annonce a bien été supprimée.'), fail_silently=True)
        return settings.LOGIN_REDIRECT_URL


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
        queryset = self.search_model.objects.filter(object_pk=self.pk)\
            .filter(content_type=content_type).filter(ad_search__public=True)
        queryset.contacted = queryset.filter(contacted=True)
        queryset.not_contacted = queryset.exclude(contacted=True)
        for obj in queryset.not_contacted:
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
    model_class = AdSearchResult
    form_class = AdSearchResultContactForm
    template_name = ""  # unused

    def form_valid(self, form):
        self.message = form.cleaned_data['message']
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        ad_search_result_id = self.kwargs['adsearchresult_id']
        # Below, tricky 'hack', depend on the context, 
        # ad_search_result_id is AdSearchResult instance or just an id ! 
        # Don't know why.
        if isinstance(ad_search_result_id, self.model_class):
            ad_search_result = ad_search_result_id
        else:
            ad_search_result = self.model_class.objects.get(id=ad_search_result_id)
        ad_search_result.contacted = True
        ad_search_result.save()
        geoad_vendor_message.send(sender=Ad, ad=ad_search_result.content_object, ad_search=ad_search_result.ad_search,
                                  user=ad_search_result.ad_search.user, message=self.message)
        return reverse('contact_buyers', kwargs={'pk': ad_search_result.object_pk})
