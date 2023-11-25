from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site


def get_site_name_domain(request=None):
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    return (site_name, domain)
