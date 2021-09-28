# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from slugify import slugify

from aptusadmin.settings import NAME_CHOICES
from aptusadmin.models.main_models import CustomUser


class Choice(models.Model):

    class Meta:
        default_permissions = ()
        unique_together = ('name', 'key')
        ordering = ['name','value']
    
    name = models.CharField('Choix', max_length=20, choices=NAME_CHOICES)
    key = models.CharField('Clé', max_length=40)
    value = models.CharField('Valeur', max_length=40)
    description = models.CharField('Description', default='', max_length=300, blank=True)

    def __str__(self):
        return f"{self.name} | {self.key}: {self.value}"

    @classmethod
    def get_elements(cls, name):
        return tuple(cls.objects.filter(name=name).values_list('key', 'value'))

    @classmethod
    def get_descriptions(cls, name):
        return cls.objects.filter(name=name).values('key', 'description')


class Label(models.Model):

    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"
        ordering = ('slug', )

    user = models.ForeignKey(CustomUser, null=True, blank=True, verbose_name="User", on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name='Content type',
    )
    label = models.CharField('Label', max_length=25)
    slug = models.CharField('Slug', max_length=256, blank=True)
    description = models.TextField('Description', default='', blank=True)
    parent = models.ForeignKey('Label', verbose_name="Parent", null=True, blank=True, related_name="child", on_delete=models.CASCADE)
    color = models.CharField('Color', max_length=25, default="#555555")

    def __str__(self):
        return self.label if not self.parent else f"{self.parent} / {self.label}"

    def get_children(self):
        return Label.objects.filter(parent=self)

    def get_all_children(self):
        return Label.objects.filter(models.Q(slug__startswith=f"{self.slug}/"))
    
    def serialize_label(self):
        return {
            'id': self.id,
            'color': self.color,
            'label': str(self),
        }
    
    def update_slug(self):
        self.slug = self.label if not self.parent else f"{self.parent.slug}/{self.label}"
        self.save()
        for child in self.get_children():
            child.update_slug()
    
    def create_label(self, model=None):
        if model:
            self.content_type = ContentType.objects.get_for_model(model)
        self.update_slug()  # This method calls self.save()
        return True, ("success", "Opération effectué avec succès.")
    
    def change_label(self):
        if self.parent == self:
            return False, ('danger', "Opération impossible.")
        if self.parent and self.parent in self.get_all_children():
            return False, ('danger', "Impossible de choisir une sous-catégorie comme parent.")
        self.update_slug()  # This method calls self.save()
        return True, ("success", "Opération effectué avec succès.")
    
    def delete_label(self):
        self.delete()
        return True, ("success", "Opération effectué avec succès.")

    @classmethod
    def get_available_labels(cls, model, user=None):
        content_type = ContentType.objects.get_for_model(model)
        user_filter = models.Q(user=None)
        if user:
            user_filter |= models.Q(user=user)
        return cls.objects.filter(user_filter, content_type=content_type)

    @classmethod
    def get_managable_labels(cls, model, user=None):
        managable_labels = cls.get_available_labels(model, user)
        if user:
            managable_labels = managable_labels.exclude(user=None)
        else:
            managable_labels = managable_labels.exclude(user__isnull=False)
        return managable_labels

    @classmethod
    def get_labels_ids(cls, model, user=None):
        labels = cls.get_available_labels(model, user)
        labels = ','.join([str(label.id) for label in labels])
        return labels
    
    @classmethod
    def get_list(cls, model, user=None):
        labels = cls.get_available_labels(model, user)
        return tuple([(label.id, label.label) for label in labels])
