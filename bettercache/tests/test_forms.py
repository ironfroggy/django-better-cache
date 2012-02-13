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

    @CachedFormMethod()
    def get_full_name(self):
        return names[self.cleaned_data['username']]


class CachedFormMethodTests(unittest.TestCase):

    def test_caches(self):
        form = SimpleForm(data={'username': 'username1'})
        self.assertEqual('User Name One', form.get_full_name())
        del names['username1']
        self.assertEqual('User Name One', form.get_full_name())
        form = SimpleForm(data={'username': 'username2'})
        self.assertEqual('User Name Two', form.get_full_name())
