import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView, UpdateView
from apps.models import TestCase, Feature
from apps.forms import TestCaseForm
import openai

from apps.service.open_ai_response import generate_test_case_chatgpt

logger = logging.getLogger(__name__)

def view_test_cases(request, feature_id):
    feature = get_object_or_404(Feature, id=feature_id)
    status_filter = request.GET.get('status')
    
    if status_filter:
        test_cases = feature.test_cases.filter(status=status_filter)
    else:
        test_cases = feature.test_cases.all()
    
    status_choices = TestCase.STATUS_CHOICES
    
    return render(request, 'view_test_cases.html', {
        'feature': feature,
        'test_cases': test_cases,
        'status_choices': status_choices,
    })

def test_case_details(request,feature_id,test_case_id):
    test_case = get_object_or_404(TestCase, id=test_case_id)
    return render(request, 'test_case_details.html', {
        'test_case': test_case,
    })

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
        return reverse_lazy('test_case_details', kwargs={'feature_id': self.object.feature.id, 'test_case_id': self.object.id})

class TestCaseUpdateView(UpdateView):
    model = TestCase
    form_class = TestCaseForm
    template_name = 'update_test_case.html'
    pk_url_kwarg = 'test_case_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feature'] = get_object_or_404(Feature, id=self.object.feature.id)
        return context

    def get_success_url(self):
        return reverse_lazy('test_case_details', kwargs={'feature_id': self.object.feature.id, 'test_case_id': self.object.id})

@csrf_exempt
def update_test_case_status(request):
    try:
        data = json.loads(request.body)
        test_case_id = data.get('test_case_id')
        new_status = data.get('new_status')
        
        if new_status not in dict(TestCase.STATUS_CHOICES).keys():
            return JsonResponse({'success': False, 'error': 'Invalid status.'})
        
        test_case = TestCase.objects.get(id=test_case_id)
        test_case.status = new_status
        test_case.save()
        
        return JsonResponse({'success': True})
    except TestCase.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Test case does not exist.'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def create_test_case_qai(request, feature_id):
    feature = get_object_or_404(Feature, id=feature_id)

    selected_test_type = request.GET.get('selected_test_type')  # Get the selected test type

    if request.method == 'POST':
        form = TestCaseForm(request.POST, selected_test_type=selected_test_type)
        if form.is_valid():
            test_case = form.save(commit=False)
            test_case.feature = feature
            test_case.test_type = selected_test_type  # Set the test type
            test_case.save()
            return redirect('test_case_details', feature_id=feature.id, test_case_id=test_case.id)

    else:
        try:
            # Call to generate test case using ChatGPT
            response = generate_test_case_chatgpt(feature, selected_test_type)

            # Assuming response is a TestCase instance
            if isinstance(response, TestCase):
                parsed_data = {
                    'title': response.title,
                    'description': response.description,
                    'steps': "\n".join(response.steps),
                    'expected_result': response.expected_result,
                }
                # Pass the selected test type as initial data
                form = TestCaseForm(initial={**parsed_data, 'test_type': selected_test_type}, selected_test_type=selected_test_type)
            else:
                logger.error("Unexpected response type from generate_test_case_chatgpt.")
                form = TestCaseForm()

        except Exception as e:
            logger.error(f"Error generating test case: {e}")
            form = TestCaseForm(selected_test_type=selected_test_type)

    return render(request, 'create_test_case_qai.html', {
        'feature': feature,
        'form': form,
        'selected_test_type': selected_test_type,  # Pass the selected test type to the template
    })