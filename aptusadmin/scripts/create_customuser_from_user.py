# -*- coding: utf-8 -*-
# python create_customuser_from_user.py
import django
django.setup()
from django.contrib.auth.models import User, Group
from myapps.models import CustomGroup, CustomUser



for user in User.objects.all():
    if not hasattr(user, 'customuser'):
        print(user, 'Created')
        customuser = CustomUser(user_ptr=user, must_change_pwd=False)
        customuser.save_base(raw=True)

for group in Group.objects.all():
    if not hasattr(group, 'customgroup'):
        print(group, 'Created')
        customgroup = CustomGroup(group_ptr=group)
        customgroup.save_base(raw=True)
print('END')