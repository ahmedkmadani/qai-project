import json
import openai
from ..models import TestCase


# Define your test case class
class TestCaseSchema:
    def __init__(self, title, description, steps, expected_result):
        self.title = title
        self.description = description
        self.steps = steps
        self.expected_result = expected_result

    def __repr__(self):
        return f"TestCase(title={self.title}, description={self.description}, steps={self.steps}, expected_result={self.expected_result})"


def get_existing_test_cases(feature_id):
    return TestCase.objects.filter(feature_id=feature_id).values('title', 'description')

def generate_test_case_chatgpt(feature, selected_test_type):
    # Retrieve existing test cases for the feature from the database
    existing_test_cases = get_existing_test_cases(feature.id)

    # Format existing test cases to include in the prompt
    existing_cases_summary = "\n".join(
        [
            f"- {case['title']}: {case['description']}"
            for case in existing_test_cases
        ]
    ) if existing_test_cases else "No existing test cases."

    # Include the class structure in the prompt
    prompt = f"""
    Generate a test case for the following feature:

    Feature Name: {feature.name}
    Description: {feature.description}
    Priority: {feature.priority}
    Status: {feature.status}
    Start Date: {feature.start_date}
    End Date: {feature.end_date}
    BRD (Functional Requirements): {feature.brd}  # Use the BRD as functional requirements
    Test Type: {selected_test_type}

    Existing Test Cases:
    {existing_cases_summary}

    The test case should be formatted as follows:
    {{
        "title": "Test Case Title",
        "description": "Detailed description of the test case.",
        "steps": [
            "Step 1: Describe a positive scenario.",
            "Step 2: Describe another positive scenario.",
            "Step 3: Describe a negative scenario.",
            "Step 4: Describe another negative scenario."
        ],
        "expected_result": "Expected outcome after executing the test steps."
    }}

    Ensure the test case complements existing ones and aligns with the BRD and feature details. Please respond in JSON format.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a test case generator for a software testing tool."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7,
            stop=None,
            response_format={"type": "json_object"}
        )

        # Extract response and parse it as a dictionary
        test_case_data = response['choices'][0]['message']['content']
        
        # Use json.loads instead of eval for safety
        test_case_dict = json.loads(test_case_data)  # Safely parse the JSON response

        # Create TestCase instance from parsed data
        test_case_instance = TestCase(
            title=test_case_dict["title"],
            description=test_case_dict["description"],
            steps=test_case_dict["steps"],
            expected_result=test_case_dict["expected_result"],
            feature=feature  # Assuming you want to link it to the feature
        )

        print(test_case_instance)
        return test_case_instance

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error generating test case: {e}")