from django.urls import path, include
from .views import CategoryViewSet, JobReadOnlyViewSet, JobDestroyView, UserJobViewSet, UserApplicationViewSet, JobApplicationsListView, JobApplicationStatusUpdateView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

user_job_create = UserJobViewSet.as_view({'post': 'create'})
user_jobs_list = UserJobViewSet.as_view({'get': 'list'})
user_jobs_retrieve = UserJobViewSet.as_view({'get': 'retrieve'})
user_jobs_update = UserJobViewSet.as_view({'put': 'update', 'patch': 'partial_update'})
user_jobs_delete = UserJobViewSet.as_view({'delete': 'destroy'})

job_list = JobReadOnlyViewSet.as_view({'get': 'list'})
job_detail = JobReadOnlyViewSet.as_view({'get': 'retrieve'})

user_applications_list_view = UserApplicationViewSet.as_view({"get": "list"})
user_applications_create_view = UserApplicationViewSet.as_view({"post": "create"})
user_applications_retrieve_view = UserApplicationViewSet.as_view({"get": "retrieve"})
user_applications_update_view = UserApplicationViewSet.as_view({"patch": "partial_update"})
user_applications_delete_view = UserApplicationViewSet.as_view({"delete": "destroy"})

urlpatterns= [
    path("jobs/", job_list, name="jobs-list"),
    path("jobs/<uuid:id>/", job_detail, name="jobs-detail"),
    ## admin
    path("admin/jobs/<uuid:id>/delete/", JobDestroyView.as_view(), name="job-destroy"),
    path('admin/category/', include(router.urls)),
    ## User job
    path('jobs/my-jobs/create/', user_job_create, name='user-crate-jobs'),
    path("jobs/my-jobs/", user_jobs_list, name="user-jobs-list"),
    path("jobs/my-jobs/<uuid:id>/", user_jobs_retrieve, name="user-jobs-detail"),
    path("jobs/my-jobs/<uuid:id>/update/", user_jobs_update, name="user-jobs-update"),
    path("jobs/my-jobs/<uuid:id>/delete/", user_jobs_delete, name="user-jobs-delete"),
    ## User applications
    path("applications/my-applications/", user_applications_list_view, name="user-applications-list"),
    path("jobs/<uuid:id>/apply", user_applications_create_view, name="user-applications-create"),
    path("applications/my-applications/<uuid:id>/", user_applications_retrieve_view, name="user-applications-retrieve"),
    path("applications/my-applications/<uuid:id>/update/", user_applications_update_view, name="user-applications-update"),
    path("applications/my-applications/<uuid:id>/delete/", user_applications_delete_view, name="user-applications-delete"),
    ## Job applications
    path("jobs/<uuid:job_id>/applications/", JobApplicationsListView.as_view(), name="job-applications-list"),
    path("applications/<uuid:id>/update-status/", JobApplicationStatusUpdateView.as_view(), name="application-update-status"),
]
