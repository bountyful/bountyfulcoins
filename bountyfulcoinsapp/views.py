from datetime import timedelta
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import (Http404, HttpResponseRedirect, HttpResponse,
                         HttpResponseBadRequest)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (View, TemplateView, CreateView,
                                  UpdateView, DetailView)
from django.views.generic.edit import BaseFormView, FormMixin

from registration.views import RegistrationView as BaseRegistrationView

from bountyfulcoinsapp.forms import (RegistrationForm, SearchForm,
                                     BountySaveForm, ImportAddressesForm,
                                     BlockChainFwdCallbackForm)
from bountyfulcoinsapp.models import (Bounty, SharedBounty, FeaturedBounty,
                                      Tag, calculate_totals)


logger = logging.getLogger('bountyfulcoinsapp.views')


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class RegistrationView(BaseRegistrationView):
    form_class = RegistrationForm

    def register(self, request, username, email, password1, **cleaned_data):
        User.objects.create_user(username=username, email=email,
                                 password=password1)

    def get_success_url(self, request=None, user=None):
        return reverse('registration_complete')


# Views for the Home Page
class HomePageView(TemplateView):
    template_name = "main_page.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            'shared_bounties': SharedBounty.objects.filter(
                disabled=False)[:50],
            'featured_bounties': FeaturedBounty.get_funded_entries(),
            'total_bounties': calculate_totals(),
        })
        return context


class AboutView(TemplateView):
    template_name = "about.html"


# View of the User Page.
def user_page(request, username):
    user = get_object_or_404(User, username=username)
    bounties = user.bounty_set.all()
    variables = RequestContext(request, {
        'bounties': bounties,
        'username': username,
        'show_tags': True,
        'show_edit': username == request.user.username,
    })
    return render_to_response('user_page.html', variables)


class BountyReusableMixin(object):
    template_name = 'bounty_save.html'
    model = Bounty
    form_class = BountySaveForm

    def get_initial(self):
        initial = super(BountyReusableMixin, self).get_initial()
        if self.object:
            initial['url'] = self.object.link.url
            tags = self.object.tags.all()
            if tags:
                initial['tags'] = ", ".join(tags.values_list('name', flat=True))
            if self.object.shared.exists():
                initial['share'] = True
            if self.object.is_featured:
                initial['featured'] = True
        return initial

    def get_success_url(self):
        if '_redirect' not in self.request.REQUEST and self.object:
            return reverse_lazy('change_bounty', args=[self.object.pk])
        return super(BountyReusableMixin, self).get_success_url()

    def form_valid(self, form):
        self.object = form.save(user=self.request.user, request=self.request)
        return HttpResponseRedirect(self.get_success_url())


class BountyCreate(LoginRequiredMixin, BountyReusableMixin, CreateView):
    pass


class BountyOwnerOnlyMixin(LoginRequiredMixin):
    def get_object(self, *args, **kwargs):
        obj = super(BountyOwnerOnlyMixin, self).get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise Http404('Could not locate the bounty')
        return obj


class BountyChange(BountyOwnerOnlyMixin, BountyReusableMixin, UpdateView):
    pass


class BountyDetails(DetailView):
    template_name = 'bounty_details.html'
    model = Bounty


class VerifyFeaturedBountyPaid(FormMixin, View):
    form_class = BlockChainFwdCallbackForm

    def get(self, request, *args, **kwargs):
        """
        Handles callback verification, instantiating a form instance with
        the passed GET variables and then checked for validity.
        """
        form_class = self.get_form_class()
        form = form_class({'data': self.request.GET})
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return HttpResponse("*ok*")  # required response by blockchain

    def form_invalid(self, form):
        error = ''
        for field, v in form.errors.items():
            error = '%s: %s' % (field, ', '.join([unicode(e) for e in v]))
        return HttpResponseBadRequest(error)  # required response by blockchain


class PopularBountiesView(TemplateView):
    template_name = 'popular_page.html'

    def get_context_data(self, **kwargs):
        context = super(PopularBountiesView, self).get_context_data(**kwargs)

        yesterday = timezone.now() - timedelta(days=1)
        context = {
            'shared_bounties': SharedBounty.objects.filter(
                date__gt=yesterday, disabled=False)[:50],
            'featured_bounties': FeaturedBounty.get_funded_entries(),
        }

        return context


def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    bounties = tag.bounties.all()
    variables = RequestContext(request, {
        'bounties': bounties,
        'tag_name': tag_name,
        'show_tags': True,
        'show_user': True
    })
    return render_to_response('tag_page.html', variables)


def tag_cloud_page(request):
    MAX_WEIGHT = 5
    tags = Tag.objects.all()
    # Calculate tag, minimum and maximum counts.
    min_count = max_count = tags[0].bounties.count()
    for tag in tags:
        tag.count = tag.bounties.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count
    # Calculate count range. Avoid dividing by zero
    range = float(max_count - min_count)
    if range == 0.0:
        range = 1.0
    # Calculate the tag weights.
    for tag in tags:
        tag.weight = int(
            MAX_WEIGHT * (tag.count - min_count) / range
        )
    variables = RequestContext(request, {
        'tags': tags
    })
    return render_to_response('tag_cloud_page.html', variables)


def search_page(request):
    form = SearchForm()
    bounties = []
    show_results = False
    if 'query' in request.GET:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            keywords = query.split()
            q = Q()
            for keyword in keywords:
                q = q & Q(title__icontains=keyword)
            form = SearchForm({'query': query})
            bounties = Bounty.objects.filter(q)[:10]
    variables = RequestContext(request, {
        'form': form,
        'bounties': bounties,
        'show_results': show_results,
        'show_tags': True,
        'show_user': True
    })
    if 'ajax' in request.GET:
        return render_to_response('bounty_list.html', variables)
    else:
        return render_to_response('search.html', variables)


@login_required
def bounty_vote_page(request):
    if 'id' in request.GET:
        try:
            id = request.GET['id']
            shared_bounties = SharedBounty.objects.get(id=id)
            user_voted = shared_bounties.users_voted.filter(
                username=request.user.username
            )
            if not user_voted:
                shared_bounties.votes += 1
                shared_bounties.users_voted.add(request.user)
                shared_bounties.save()
        except SharedBounty.DoesNotExist:
            raise Http404('Bounty not found')
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect('/')


class ImportAddressView(BaseFormView):
    success_url = reverse_lazy('admin:bountyfulcoinsapp_address_changelist')
    form_class = ImportAddressesForm
    http_method_names = ['post']
    filetype = 'csv'  # default to csv

    def form_valid(self, form):
        """
        If the form is valid, save the file data into db.
        """
        form.save_addresses()
        messages.add_message(
            self.request, messages.SUCCESS,
            _('Succesfully imported addresses form file.')
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is valid, save the file data into db.
        """
        for field, v in form.errors.items():
            error = '%s: %s' % (field, ', '.join([unicode(e) for e in v]))
            messages.add_message(
                self.request, messages.ERROR,
                error
            )
        return HttpResponseRedirect(self.get_success_url())
