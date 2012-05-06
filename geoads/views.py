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
from django.contrib.gis.utils import GeoIP
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import QueryDict, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView


from geoads.models import Ad, AdSearch, AdPicture
from geoads.forms import AdPictureForm, AdContactForm, BaseAdForm


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

'''
TODO: add this tip to center map on load
def get_client_ip(request):
    """
    Get client IP, used to localize client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
'''

def account_url(request):
    try:
        url = settings.ADS_PROFILE_URL % (request.user.username)
    except:
        url = settings.ADS_PROFILE_URL
    return url

class AdSearchView(ListView):
    """
    Class based ad search view

    Not really clean, get-post condition in the above functions
    """
    model = Ad
    filterset_class = None
    search_id = None
    template_name = 'geoads/search.html'
    context_object_name = 'filter'
    search_id = None
    
    def get_queryset(self):
        # HACK, getattr doesn't work ! don't know why
        try:
            self.search_id = self.kwargs['search_id']
        except:
            self.search_id = None
        if self.request.method != 'POST' and self.request.GET == {} and self.search_id is None:
            search = False
            filter = self.filterset_class(None, search=search)
        else:
            search = True
            if self.search_id is not None:
                ad_search = AdSearch.objects.get(id = self.search_id)
                if ad_search.user != self.request.user:
                    raise Http404
                q = QueryDict(ad_search.search)
                filter = self.filterset_class(q or None, search=search)
            else:
                filter = self.filterset_class(self.request.POST or None, search=search)
            ### lot of case here, need to clean
            if self.request.POST.__contains__('save_and_search') and self.search_id is None:
                datas = self.request.POST.copy()
                del datas['save_and_search']
                del datas['csrfmiddlewaretoken']
                search =  datas.urlencode()
                user = self.request.user
                ad_search = AdSearch(search = search,
                         content_type = ContentType.objects.get_for_model(self.model), 
                         user = user)
                ad_search.save()
                userena_profile_detail_url = account_url(self.request)
                messages.add_message(self.request, messages.INFO,
                _(u'Votre recherche a bien été sauvegardée '+
                  u'dans <a href="%s">votre compte</a>.') 
                % (userena_profile_detail_url))
            # len method is faster than count() in this case !
            try:
                nb_of_results = len(filter.qs)
            except:
                nb_of_results = 0
            if nb_of_results == 0:
                messages.add_message(self.request, messages.INFO, 
                _(u'Aucune annonce ne correspond à votre recherche. '+
                  u'Elargissez votre zone de recherche ou modifiez les critères.'))
            if nb_of_results >= 1:
                ann = _(u'annonces')
                if nb_of_results == 1:
                    ann = _(u'annonce')
                if self.request.user.is_authenticated():
                    messages.add_message(self.request, messages.INFO, 
                                 _(u'%s %s correspondant à votre recherche') % 
                                  (nb_of_results, ann))
                else:
                    sign_url = settings.ADS_PROFILE_SIGNUP
                    messages.add_message(self.request, messages.INFO, 
                          _(u'%s %s correspondant à votre recherche. '+ 
                            u'<a href="%s">Inscrivez-vous</a> pour recevoir'+ 
                            u' les alertes mail ou enregistrer votre recherche.') \
                               % (nb_of_results, ann, sign_url))
        return filter

    def post(self, request, *args, **kwargs):
        # hack for a kind of post to get dispath
        # but not sure it works ...
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
        return context

class AdSearchDeleteView(DeleteView):
    """
    Class based delete search ad
    """
    model = AdSearch
    
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
    model = Ad # changed in urls
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
            instance = contact_form.save(commit = False)
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
        return render_to_response(self.template_name, {'ad':self.get_object(), 
                                  'contact_form':contact_form, 
                                  'sent_mail':sent_mail}, 
                                  context_instance = RequestContext(request))

    def get_queryset(self):
        # below should return moderated objects w/ django-moderation
        return self.model.objects.all()

class AdCreateView(LoginRequiredMixin, CreateView):
    """
    Class based create ad
    """
    model = Ad # overriden in specific project urls
    template_name = 'geoads/edit.html'
    
    def form_valid(self, form):
        context = self.get_context_data()
        picture_formset = context['picture_formset']
        if picture_formset.is_valid():
            self.object = form.save(commit = False)
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
                                  {'site_name':Site.objects.get_current().name})
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
            PictureFormset = generic_inlineformset_factory(AdPicture, 
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset(self.request.POST, 
                                                        self.request.FILES)
        else:
            PictureFormset = generic_inlineformset_factory(AdPicture, 
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset()
        return context


class AdUpdateView(LoginRequiredMixin, UpdateView):
    """
    Class base update ad
    """
    model = Ad # overriden in specific project urls
    template_name = 'geoads/edit.html'

    def form_valid(self, form):
        context = self.get_context_data()
        picture_formset = context['picture_formset']
        if picture_formset.is_valid():
            self.object = form.save(commit = False)
            self.object.location = form.cleaned_data['location']
            self.object.address = form.cleaned_data['address']
            self.object.save()
            picture_formset.instance = self.object
            picture_formset.save()
            message = render_to_string(
                              'geoads/emails/ad_update_email_message.txt', {})
            subject = render_to_string(
                              'geoads/emails/ad_update_email_subject.txt', 
                             {'site_name':Site.objects.get_current().name})
            send_mail(subject, message, 'contact@achetersanscom.com', 
                          [self.object.user.email], 
                          fail_silently=True)
            return redirect('complete', permanent=True)
        #TODO: if formset not valid
        
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = self.model.unmoderated_objects.get(id = self.kwargs['pk'])
        if not obj.user == self.request.user:
            raise Http404
        # TODO: ugly hack don't understand, if not line below, value is converted
        obj.location = str(obj.location)
        return obj

    def get_context_data(self, **kwargs):
        context = super(AdUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            PictureFormset = generic_inlineformset_factory(AdPicture, 
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset(self.request.POST, 
                                                  self.request.FILES,
                                                  instance = context['object'])
        else:
            PictureFormset = generic_inlineformset_factory(AdPicture, 
                                                   extra=4, max_num=4)
            context['picture_formset'] = PictureFormset(instance = context['object'])
        return context


class CompleteView(LoginRequiredMixin, TemplateView):
    template_name = "geoads/validation.html"

class AdDeleteView(LoginRequiredMixin, DeleteView):
    """
    Class based delete ad
    """
    model = Ad # "normally" overrided in specific project urls
    template_name = "geoads/ad_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete_date = datetime.now()
        self.object.save()
        serialized_obj = serializers.serialize('json', [ self.object, ])
        path = default_storage.save('deleted/%s-%s.json' % (self.object.id, 
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