from bettercache.objects import CacheModel, Field, Key
from bettercache.forms import CachedFormMethod

from django import forms

import unittest

names = {
    'username1': 'User Name One',
    'username2': 'User Name Two',
}


class SimpleForm(forms.Form):

    username = forms.CharField(required=True)

    @CachedFormMethod.cache()
    def get_full_name(self):
        return names[self.cleaned_data['username']]


class CachedFormMethodTests(unittest.TestCase):

    def test_caches(self):
        form1 = SimpleForm(data={'username': 'username1'})
        form2 = SimpleForm(data={'username': 'username2'})

        self.assertEqual('User Name One', form1.get_full_name())
        self.assertEqual('User Name Two', form2.get_full_name())

        names.clear()

        self.assertEqual('User Name One', form1.get_full_name())
        self.assertEqual('User Name Two', form2.get_full_name())
