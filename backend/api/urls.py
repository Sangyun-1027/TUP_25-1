from django.urls import path
from .views import *

urlpatterns = [
    # 팀
    path('teams/', TeamListView.as_view(), name='team-list'),  # GET: 팀 목록
    path('teams/create/', TeamCreateView.as_view(), name='team-create'),  # POST: 팀 생성
    path('teams/<int:team_id>/', TeamDetailView.as_view(), name='team-detail'),  # GET: 팀 상세
    path('teams/<int:team_id>/apply/', TeamApplyView.as_view(), name='team-apply'),  # POST: 팀 지원
    path('teams/<int:team_id>/invite/', InviteUserView.as_view(), name='team-invite'),  # POST: 팀 초대


    # 초대
    path('invitations/<int:invite_id>/accept/', AcceptInviteView.as_view(), name='accept-invite'),  # POST
    path('invitations/<int:invite_id>/reject/', RejectInviteView.as_view(), name='reject-invite'),  # POST
    path('my-invites/', MyInvitesView.as_view(), name='my-invites'),  # GET: 받은 초대 목록

    # 신청
    path('applications/<int:application_id>/accept/', AcceptApplicationView.as_view(), name='accept-application'),  # POST
    path('applications/<int:application_id>/reject/', RejectApplicationView.as_view(), name='reject-application'),  # POST
    path('my-applications/', MyApplicationsView.as_view(), name='my-applications'),  # GET: 내가 지원한 목록

    # 유저 필터링 
    path('applicants/filter/', ApplicantFilterView.as_view(), name='applicant-filter'),
]

