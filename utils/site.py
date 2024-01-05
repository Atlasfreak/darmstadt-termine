from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest


def get_site_name_domain(request: HttpRequest = None):
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    return (site_name, domain)
