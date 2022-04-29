from django.urls import reverse_lazy
from django.views.generic import CreateView

from users import forms


class SignUp(CreateView):
    form_class = forms.CreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
