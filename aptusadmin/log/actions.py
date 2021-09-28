# -*- encoding: utf-8 -*-

# --------------------------
# Ripped from django project
# --------------------------

from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text


def log_addition(object, user, message=''):
    """
    Log that an object has been successfully added.
    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, ADDITION
    LogEntry.objects.log_action(
        user_id=user.id,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        # object_repr=force_text(object),  ##Permet d'afficher le str dans l'objet
        object_repr=object.log_text(),
        change_message=message,
        action_flag=ADDITION
    )


def log_change(object, user, message):
    """
    Log that an object has been successfully changed.
    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, CHANGE
    LogEntry.objects.log_action(
        user_id=user.id,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        #object_repr=force_text(object), ##Permet d'afficher le str dans l'objet 
        object_repr=object.log_text(),
        action_flag=CHANGE,
        change_message=message
    )


def log_deletion(object, user, message=''):
    """
    Log that an object will be deleted. Note that this method is called
    before the deletion.

    The default implementation creates an admin LogEntry object.
    """
    from django.contrib.admin.models import LogEntry, DELETION
    LogEntry.objects.log_action(
        user_id=user.id,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        #object_repr=force_text(object),  ##Permet d'afficher le str dans l'objet 
        object_repr=object.log_text(),
        change_message=message,
        action_flag=DELETION,
    )
