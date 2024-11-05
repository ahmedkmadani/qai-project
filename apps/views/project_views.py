from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from apps.models import Project
from apps.forms import ProjectForm
from django.views.generic.edit import CreateView

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})

def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    features = project.features.all()
    return render(request, 'project_details.html', {'project': project, 'features': features, 'project_id': project_id})

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'create_project.html'
    success_url = reverse_lazy('projects') 

    def form_valid(self, form):
        form.instance.manager = self.request.user
        return super().form_valid(form)
