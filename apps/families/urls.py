from django.urls import path
from django.urls import path, include
from . import views

app_name = 'families'

urlpatterns = [
    path('list/', views.FamilyListView.as_view(), name='list'),
    path('create/', views.FamilyCreateView.as_view(), name='create'),
    path('join/', views.JoinByCodeView.as_view(), name='join'),
    path('<int:pk>/', views.FamilyDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.FamilyUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.FamilyDeleteView.as_view(), name='delete'),
    path('<int:family_id>/people/', include('apps.persons.urls', namespace='persons')),   # <<-- important: family_id forwarded
    path('<int:pk>/members/', views.MembersManageView.as_view(), name='members'),
    path('<int:pk>/members/approve/<int:jr_pk>/', views.ApproveJoinRequestView.as_view(), name='approve_join'),
    path('<int:pk>/members/reject/<int:jr_pk>/', views.RejectJoinRequestView.as_view(), name='reject_join'),
    path('<int:pk>/members/remove/<int:member_id>/', views.RemoveMemberView.as_view(), name='remove_member'),
    path('<int:pk>/members/change-role/<int:member_id>/',views.ChangeMemberRoleView.as_view(), name='change_role'),
    # Invitations
    path('<int:pk>/invite/', views.invite_member, name='invite'),
    path('accept-invite/', views.AcceptInviteView.as_view(), name='accept_invite'),
    path('<int:family_id>/tree/', include('apps.tree.urls',namespace='tree_per_family')),
]
