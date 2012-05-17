from bettercache.objects import CacheModel, Field, Key
from bettercache.decorators import CachedFormMethod

from django import forms

import unittest

names = {
    'username1': 'User Name One',
    'username2': 'User Name Two',
}


class SimpleForm(forms.Form):

    username = forms.CharField(required=True)

    @CachedFormMethod.cache()
    def get_full_name(self, skip_middle=False):
        full_name = names[self.cleaned_data['username']].split()
        if skip_middle:
            del full_name[1]
        return ' '.join(full_name)


class CachedFormMethodTests(unittest.TestCase):

    def test_caches(self):
        form1 = SimpleForm(data={'username': 'username1'})
        form2 = SimpleForm(data={'username': 'username2'})

        form1.is_valid()
        form2.is_valid()

        self.assertEqual('User Name One', form1.get_full_name())
        self.assertEqual('User Name Two', form2.get_full_name())
        self.assertEqual('User Two', form2.get_full_name(skip_middle=True))

        names.clear()

        self.assertEqual('User Name One', form1.get_full_name())
        self.assertEqual('User Name Two', form2.get_full_name())
