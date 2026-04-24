from django import template
from core.tenancy import get_company_user as _get_cu, get_company as _get_co

register = template.Library()

@register.simple_tag
def get_company_user(user):
    return _get_cu(user)

@register.simple_tag
def get_company(user):
    return _get_co(user)
