import os

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from bountyfulcoinsapp import views

site_media = os.path.join(
    os.path.dirname(__file__), 'site_media'
)

admin.autodiscover()

urlpatterns = patterns(
    '',

    # Browsing
    url(r'^$', views.HomePageView.as_view(), name='main_page'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^popular/$', views.PopularBountiesView.as_view(), name='popular'),

    # FIXME: Refactor points: CBV ME!
    url(r'^user/(\w+)/$', views.user_page, name='user_page'),
    url(r'^tag/([^\s]+)/$', views.tag_page, name='tag'),
    url(r'^tag/$', views.tag_cloud_page, name='tag_cloud'),

    # Session and user management
    url(r'^register/$', views.RegistrationView.as_view(),
        name='registration_register'),
    url(r'', include('registration.backends.default.urls')),
    url(r'^comments/', include('django_comments_xtd.urls')),

    # Content Management
    url(r'^bounty/$', views.BountyCreate.as_view(), name='create_bounty'),
    url(r'^bounty/(?P<pk>\d+)$', views.BountyChange.as_view(),
        name='change_bounty'),
    url(r'^bounty/(?P<pk>\d+)/details$', views.BountyDetails.as_view(),
        name='bounty_details'),
    url(r'^admin/bountyfulcoinsapp/address/import/$',
        views.ImportAddressView.as_view(filetype='csv'),
        name='import_address_csv'),
    url(r'^search/$', views.search_page, name='search'),
    url(r'^vote/$', views.bounty_vote_page),

    # endpoints for blockchain api
    url(r'^callback/$', views.VerifyFeaturedBountyPaid.as_view(),
        name='callback'),

    # Django Admin Page
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # Site Media
    urlpatterns += url(
        r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': site_media}),
