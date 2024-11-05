from django.conf import settings
from django.shortcuts import get_object_or_404, render
from ..models import TestCase, Feature
import openai  # Make sure to install the OpenAI library
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os


openai.api_key = settings.OPENAI_API_KEY

def generate_code_view(request, feature_id, test_case_id):
    # Retrieve the test case and feature
    test_case = get_object_or_404(TestCase, id=test_case_id)
    feature = get_object_or_404(Feature, id=feature_id)

    # Prepare the prompt for the AI model
    prompt = f"Generate Selenium automation code for the following test case:\n\n" \
             f"Title: {test_case.title}\n" \
             f"Description: {test_case.description}\n" \
             f"Steps: {test_case.steps}\n" \
             f"Expected Result: {test_case.expected_result}\n" \
             f"Feature: {feature.name}\n\n" \
             f"Please provide the code in Python using Selenium."

    # Call the AI model to generate the code
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the appropriate model
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        generated_code = response['choices'][0]['message']['content'].replace('```python', '').replace('```', '').strip()
    except Exception as e:
        generated_code = f"Error generating code: {str(e)}"

    # Render the generated code in a template
    return render(request, 'generated_code_view.html', {
        'test_case': test_case,
        'generated_code': generated_code,
    })
    
    


@csrf_exempt  # Disable CSRF for this example (not recommended for production)
def execute_code(request):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        
        # Save the code to a temporary Python file
        with open('temp_script.py', 'w') as f:
            f.write(code)

        # Execute the code using subprocess
        try:
            os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
            result = subprocess.run(['python', 'temp_script.py'], capture_output=True, text=True, check=True)
            output = result.stdout
        except subprocess.CalledProcessError as e:
            output = e.stderr
            
            # Send the error to ChatGPT for analysis and get new code
            prompt = f"Here is the error message:\n{output}\n\nPlease provide a corrected version of the following code:\n{code}"
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                new_code = response['choices'][0]['message']['content']
                
                # Overwrite the previous code with the new code
                with open('temp_script.py', 'w') as f:
                    f.write(new_code)
                
                # Execute the new code
                result = subprocess.run(['python', 'temp_script.py'], capture_output=True, text=True, check=True)
                output = result.stdout
            except subprocess.CalledProcessError as e:
                output = f"Error executing the corrected code: {e.stderr}"
            except Exception as chatgpt_error:
                output = f"Error contacting ChatGPT: {str(chatgpt_error)}"

        return JsonResponse({'output': output})
    return JsonResponse({'error': 'Invalid request'}, status=400)