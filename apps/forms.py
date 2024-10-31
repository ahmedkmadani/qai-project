# forms.py

from django import forms
from .models import Feature, Project, TestCase

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'version']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter project description'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1.0'}),
        }


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        exclude = ['project']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter feature name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter feature description'}),
            'brd': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Enter BRD'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        

class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        exclude = ['feature', 'created_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter test case title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter steps'}),
            'expected_result': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter expected result'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    status = forms.ChoiceField(
        choices=TestCase.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='NEW',
    )