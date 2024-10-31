from django.urls import path
from apps.views.project_views import project_list, project_details, ProjectCreateView
from apps.views.feature_views import FeatureCreateView
from apps.views.test_case_views import (
    view_test_cases,
    test_case_details,
    TestCaseCreateView,
    TestCaseUpdateView,
    update_test_case_status,
    create_test_case_qai
)

urlpatterns = [
    path('', project_list, name='projects'),
    path('projects/<int:project_id>/', project_details, name='project_details'),
    path('projects/create/', ProjectCreateView.as_view(), name='create_project'),
    path('projects/<int:project_id>/features/create/', FeatureCreateView.as_view(), name='create_feature'),
    path('features/<int:feature_id>/test-cases/', view_test_cases, name='view_test_cases'),
    path('features/<int:feature_id>/test-cases/create/', TestCaseCreateView.as_view(), name='create_test_case'),
    path('features/<int:feature_id>/test-cases/<int:test_case_id>/', test_case_details, name='test_case_details'),
    path('features/<int:feature_id>/test-cases/<int:test_case_id>/update/',TestCaseUpdateView.as_view(),name='update_test_case'),
    path('ajax/update-test-case-status/', update_test_case_status, name='update_test_case_status'),
    path('features/<int:feature_id>/test-cases/qai/', create_test_case_qai, name='create_test_case_qai'),
]
