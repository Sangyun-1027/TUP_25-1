from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Team, User, Application, Invitation
from .serializers import TeamSerializer
from django.db.models import Prefetch
from .serializers import UserSerializer  

# 1. 팀 생성
class TeamCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        team = Team.objects.create(
            leader=request.user,
            tech=data.get('tech', []),
            looking_for=data.get('looking_for', []),
            max_members=data.get('max_members'),
        )
        team.members.add(request.user)
        return Response({'id': team.id}, status=201)

# 2. 유저 정보 수정 (User 모델 직접 수정)
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user
        user.skills = data.get('skills', [])
        user.keywords = data.get('keywords', [])
        user.mainRole = data.get('mainRole', '')
        user.subRole = data.get('subRole', '')
        user.name = data.get('name', user.name)
        user.save()
        return Response({'status': 'updated'}, status=200)

# 3. 팀 신청
class TeamApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        Application.objects.create(team=team, user=request.user, status='pending')
        return Response({'status': 'applied'}, status=201)

# 4. 초대 수락/거절
class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_id):
        invite = get_object_or_404(Invitation, id=invite_id, user=request.user)
        invite.team.members.add(request.user)
        invite.status = 'accepted'
        invite.save()
        return Response({'status': 'accepted'})

class RejectInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invite_id):
        invite = get_object_or_404(Invitation, id=invite_id, user=request.user)
        invite.status = 'rejected'
        invite.save()
        return Response({'status': 'rejected'})

# 5. 신청 수락/거절
class AcceptApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        app = get_object_or_404(Application, id=application_id)
        if app.team.leader != request.user:
            return Response({'error': '권한 없음'}, status=403)
        app.team.members.add(app.user)
        app.status = 'accepted'
        app.save()
        return Response({'status': 'accepted'})

class RejectApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        app = get_object_or_404(Application, id=application_id)
        if app.team.leader != request.user:
            return Response({'error': '권한 없음'}, status=403)
        app.status = 'rejected'
        app.save()
        return Response({'status': 'rejected'})

# 6. 초대 보내기
class InviteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        if team.leader != request.user:
            return Response({'error': '권한 없음'}, status=403)
        user = get_object_or_404(User, id=request.data['user_id'])
        Invitation.objects.create(team=team, user=user, status='pending')
        return Response({'status': 'invited'})

# 7. 팀 리스트 (리워드 우선 정렬)
class TeamListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teams = Team.objects.prefetch_related('members').select_related('leader').all()
        team_with_flags = []

        for team in teams:
            has_reward = False
            if team.leader.has_reward:
                has_reward = True
            else:
                for member in team.members.all():
                    if member.has_reward:
                        has_reward = True
                        break
            team_with_flags.append((has_reward, team))

        sorted_teams = sorted(team_with_flags, key=lambda x: (not x[0], x[1].id))
        sorted_team_objects = [t[1] for t in sorted_teams]

        serializer = TeamSerializer(sorted_team_objects, many=True)
        return Response(serializer.data)

# 8. 팀 상세
class TeamDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, team_id):
        team = get_object_or_404(
            Team.objects.prefetch_related('members', 'application_set__user'),
            id=team_id
        )
        serializer = TeamSerializer(team)
        return Response(serializer.data)

# 9. 내 초대 내역
class MyInvitesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invites = Invitation.objects.filter(user=request.user).select_related('team')
        data = [
            {
                'id': invite.id,
                'team': invite.team.id,
                'status': invite.status
            }
            for invite in invites
        ]
        return Response(data)

# 10. 내가 신청한 팀들
class MyApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        apps = Application.objects.filter(user=request.user).select_related('team')
        data = [
            {
                'id': app.id,
                'team': app.team.id,
                'status': app.status
            }
            for app in apps
        ]
        return Response(data)


# 11. 역할 기술 평점 순 필터링
class ApplicantFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.query_params.get('role', '')
        skill = request.query_params.get('skill', '')
        min_rating = request.query_params.get('min_rating', '')

        users = User.objects.all()

        # 역할 필터
        if role:
            users = users.filter(mainRole__icontains=role)

        # 기술 스택 필터 (ArrayField 또는 CharField 기준 다르게 처리)
        if skill:
            users = users.filter(skills__icontains=skill)  # skills가 CharField일 경우

        # 평점 필터
        if min_rating:
            try:
                min_rating = float(min_rating)
                users = users.filter(rating__gte=min_rating)
            except ValueError:
                pass  # 숫자가 아닐 경우 무시

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)