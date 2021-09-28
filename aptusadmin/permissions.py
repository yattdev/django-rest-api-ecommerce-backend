# -*- coding: utf-8 -*-
def viewlist_customuser(user):
    return user.has_perm('aptusadmin.viewlist_customuser')


def view_customuser(user):
    return user.has_perm('aptusadmin.view_customuser')


def add_customuser(user):
    return user.has_perm('aptusadmin.add_customuser')


def delete_customuser(user):
    return user.has_perm('aptusadmin.delete_customuser')


def change_customuser(user):
    return user.has_perm('aptusadmin.change_customuser')


def can_take_identity(user):
    return user.has_perm('aptusadmin.can_take_identity')


def import_permission(user):
    return user.has_perm('aptusadmin.importpermission_customuser')


def export_permission(user):
    return user.has_perm('aptusadmin.exportpermission_customuser')


#########################################################
def viewlist_customgroup(user):
    return user.has_perm('aptusadmin.viewlist_customgroup')


def view_customgroup(user):
    return user.has_perm('aptusadmin.view_customgroup')


def add_customgroup(user):
    return user.has_perm('aptusadmin.add_customgroup')


def delete_customgroup(user):
    return user.has_perm('aptusadmin.delete_customgroup')


def change_customgroup(user):
    return user.has_perm('aptusadmin.change_customgroup')


#########################################################
def viewlist_apis(user):
    return user.has_perm('aptusadmin.viewlist_api')
