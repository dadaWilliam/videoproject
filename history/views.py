from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from django.views.generic.detail import SingleObjectMixin
from helpers import get_page_list

from .models import History

class HistoryList(ListView):
    model = History
    template_name = 'history/history_list.html'
    paginate_by = 8
    context_object_name = 'history_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        page_list = get_page_list(paginator, page)
        # classification_list = Classification.objects.filter(status=True).values()
        # context['c'] = self.c
        # context['classification_list'] = classification_list
        context['page_list'] = page_list
        return context

    def get_queryset(self):
        user_history = History.objects.filter(user=self.request.user).order_by('-viewed_on')
        return user_history


class HistoryDelete(SingleObjectMixin, View):
    model = History
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is not None:
            obj.delete()
        return redirect('history')
