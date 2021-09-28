# -*- coding: utf-8 -*-
from datetime import timedelta

from django import template
from django.db import models
from os.path import dirname, basename
from furl import furl

from aptusadmin.settings import UTC_PLUS, VERBOSE_NAME

register = template.Library()


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


def get_field_verbose_name(instance, arg):
    return instance._meta.get_field(arg).verbose_name
register.filter('field_verbose_name', get_field_verbose_name)


@register.filter
def plural_verbose_name(instance):
    return instance._meta.verbose_name_plural.title()


@register.filter
def custom_verbose_name(instance):
    return VERBOSE_NAME.get(instance, instance)


def get_dirname(path):
    if len(path.split('?')) > 1: 
        params = path.split('?')[1]
        full_path = dirname(dirname(path.split('?')[0])) + '/?' + params
    else:
        full_path = dirname(dirname(path))+'/'
    return full_path
register.filter('dirname', get_dirname)


def get_basename(path):
    var = path.split('?')[0]
    base_name = basename(dirname(var))
    return base_name
register.filter('basename', get_basename)


def add_name(path, name):
    if len(path.split('?')) > 1: 
        full_path = path.split('?')[0] +str(name)+'?' + path.split('?')[1]
    else:
        full_path = path + str(name)
    return full_path
register.filter('addname', add_name)


def change_page(path, nbr):
    new_nbr = str(nbr)
    f = furl(path)
    try:
        old_nbr = f.args['page']
        new_path = path.replace("page="+old_nbr, "page="+new_nbr)
    except KeyError:
        if '?' not in path:
            new_path = path + "?" + "page="+new_nbr
        else:
            new_path = path + "&" + "page="+new_nbr
    return new_path
register.filter('page', change_page)


def convert_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    str_h = str(int(h))+' h ' if h != 0 else ''
    str_m = str(int(m))+' min ' if m != 0 else ''
    str_s = str(int(s))+' sec ' if s != 0 else ''
    r_str = str_h + str_m + str_s 
    if r_str == '':
        r_str = '0 h'
        
    return r_str
register.filter('strduree', convert_seconds)


def get_customgroups(customuser):
    list = []
    qset = customuser.get_customgroups()
    for elt in qset:
        list.append(str(elt))
    return  '|'.join(list)
register.filter('customgroups', get_customgroups)


def get_action_flag_verbose_name(instance):
    if instance.action_flag == 1:
        r = 'Création'
    elif instance.action_flag == 2:
        r = 'Modification'
    elif instance.action_flag == 3:
        r = 'Suppression'
    return r
register.filter('action_flag_verbose_name', get_action_flag_verbose_name)


def localize(date):
    return date + timedelta(hours=UTC_PLUS)
register.filter('localize', localize)


def delocalize(date):
    return date + timedelta(hours=-UTC_PLUS)
register.filter('delocalize', delocalize)


@register.filter
def subtract(value, arg):
    f1 = float(value)
    f2 = float(arg)
    return str(f1 - f2).replace(',', '.')


@register.filter
def multiply(value, arg):
    return value * arg


@register.simple_tag 
def get_verbose_name(object, plural=False):
    if plural:
        return object._meta.verbose_name_plural
    else: 
        return object._meta.verbose_name
