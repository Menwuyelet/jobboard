from django.urls import path, include
from .views import CategoryViewSet, JobReadOnlyViewSet, JobDestroyView, UserJobViewSet
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
]
