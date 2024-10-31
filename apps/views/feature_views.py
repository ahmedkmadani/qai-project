from django.shortcuts import render, get_object_or_404, redirect
from apps.models import Feature, Project
from apps.forms import FeatureForm
from django.views.generic import CreateView
from django.urls import reverse_lazy

class FeatureCreateView(CreateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'create_feature.html'

    def form_valid(self, form):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        form.instance.project = project
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        context['project'] = get_object_or_404(Project, id=project_id)
        return context

    def get_success_url(self):
        return reverse_lazy('project_details', kwargs={'project_id': self.object.project.id})
