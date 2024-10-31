import json
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.forms import FeatureForm, ProjectForm, TestCaseForm
from apps.models import Feature, Project, TestCase
from django.views.generic.edit import CreateView
import openai
import logging
import re
from django.views.generic import UpdateView
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Optional if using CSRF token via JavaScript
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

openai.api_key = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Define a structured object for the test case
class TestCaseData:
    def __init__(self, title='', description='', steps='', expected_result=''):
        self.title = title
        self.description = description
        self.steps = steps
        self.expected_result = expected_result

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'steps': self.steps,
            'expected_result': self.expected_result
        }

def extract_json(content):
    """
    Extract JSON from the response using regex to find content within code blocks.
    """
    json_pattern = re.compile(r"```json(.*?)```", re.DOTALL)
    match = json_pattern.search(content)
    if match:
        json_str = match.group(1).strip()
        return json_str
    else:
        # If no code block is found, assume the entire content is JSON
        return content.strip()

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})

def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    features = project.features.all()
    return render(request, 'project_details.html', {'project': project, 'features': features})

    
def view_test_cases(request, feature_id):
    feature = get_object_or_404(Feature, id=feature_id)
    status_filter = request.GET.get('status')
    
    if status_filter:
        test_cases = feature.test_cases.filter(status=status_filter)
    else:
        test_cases = feature.test_cases.all()
    
    # Pass STATUS_CHOICES to the template
    status_choices = TestCase.STATUS_CHOICES
    
    return render(request, 'view_test_cases.html', {
        'feature': feature,
        'test_cases': test_cases,
        'status_choices': status_choices,
    })
    
def test_case_details(request, test_case_id):
    test_case = get_object_or_404(TestCase, id=test_case_id)
    return render(request, 'test_case_details.html', {
        'test_case': test_case,
    })
    
def create_test_case_qai(request, feature_id):
    feature = get_object_or_404(Feature, id=feature_id)

    if request.method == 'POST':
        form = TestCaseForm(request.POST)
        if form.is_valid():
            # Save the form as a new TestCase linked to the feature
            test_case = form.save(commit=False)
            test_case.feature = feature
            test_case.save()
            return redirect('feature_details', feature_id=feature.id)
    else:
        # Compose the prompt for ChatGPT
        prompt = f"""
Generate a test case for the following feature in JSON format:

Feature Name: {feature.name}
Description: {feature.description}
Priority: {feature.priority}
Status: {feature.status}
Start Date: {feature.start_date}
End Date: {feature.end_date}

The JSON should include the following fields:
- title
- description
- steps
- expected_result

Example Format:
{{
    "title": "Test Case Title",
    "description": "Detailed description of the test case.",
    "steps": "Step 1...\nStep 2...",
    "expected_result": "Expected outcome."
}}
"""

        try:
            # Send the prompt to ChatGPT using the ChatCompletion API
            response = openai.ChatCompletion.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are an assistant that generates structured test cases in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                n=1,
                stop=None,
            )

            # Extract the response content
            generated_test_case = response.choices[0].message['content'].strip()
            json_str = extract_json(generated_test_case)

            # Attempt to parse the JSON response
            try:
                test_case_data = json.loads(json_str)
            except json.JSONDecodeError:
                # Handle JSON parsing errors
                test_case_data = {
                    'title': '',
                    'description': '',
                    'steps': '',
                    'expected_result': ''
                }
                logger.error("Error parsing JSON from ChatGPT response.")

            # Pre-fill the form with the generated test case data
            form = TestCaseForm(initial=test_case_data)

        except Exception as e:
            # Handle any errors that occur during the API call
            form = TestCaseForm()  # Fallback to an empty form
            logger.error(f"Error generating test case: {e}")

    return render(request, 'create_test_case_qai.html', {
        'feature': feature,
        'form': form,
    })


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'create_project.html'
    success_url = reverse_lazy('projects') 

    def form_valid(self, form):
        # Set the manager to the current user
        form.instance.manager = self.request.user
        return super().form_valid(form)


class FeatureCreateView(CreateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'create_feature.html'

    def form_valid(self, form):
        # Assign the feature to the correct project
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        form.instance.project = project
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Pass the project to the template context
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        context['project'] = get_object_or_404(Project, id=project_id)
        return context

    def get_success_url(self):
        # Redirect to the project details page after successful creation
        return reverse_lazy('project_details', kwargs={'project_id': self.object.project.id})
    
    
class TestCaseCreateView(CreateView):
    model = TestCase
    form_class = TestCaseForm
    template_name = 'create_test_case.html'

    def form_valid(self, form):
        feature_id = self.kwargs['feature_id']
        feature = get_object_or_404(Feature, id=feature_id)
        form.instance.feature = feature
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feature_id = self.kwargs['feature_id']
        context['feature'] = get_object_or_404(Feature, id=feature_id)
        return context

    def get_success_url(self):
        return reverse_lazy('feature_details', kwargs={'feature_id': self.object.feature.id})
    
    
class TestCaseUpdateView(UpdateView):
    model = TestCase
    form_class = TestCaseForm
    template_name = 'update_test_case.html'
    
    def get_success_url(self):
        return reverse_lazy('test_case_details', kwargs={'test_case_id': self.object.id})
   
    
@require_POST
def update_test_case_status(request):
    try:
        data = json.loads(request.body)
        test_case_id = data.get('test_case_id')
        new_status = data.get('new_status')
        
        # Validate new_status
        if new_status not in dict(TestCase.STATUS_CHOICES).keys():
            return JsonResponse({'success': False, 'error': 'Invalid status.'})
        
        # Fetch the test case
        test_case = TestCase.objects.get(id=test_case_id)
        
        # Update the status
        test_case.status = new_status
        test_case.save()
        
        return JsonResponse({'success': True})
    except TestCase.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Test case does not exist.'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})