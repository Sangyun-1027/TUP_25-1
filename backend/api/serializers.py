from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, Application, Invitation, UserProfile

# ✅ 사용자 프로필 모델 시리얼라이저
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'realname', 'skills', 'role']  # 필요한 필드만 선택적으로 지정

# ✅ User 모델을 간단히 나타내는 시리얼라이저 (UserProfile 포함)
class SimpleUserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'userprofile']

# ✅ 팀 신청 시리얼라이저
class ApplicationSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)  # 신청자 정보 포함

    class Meta:
        model = Application
        fields = ['id', 'user', 'status']  # 신청 ID, 유저 정보, 상태 ('pending', 'accepted', ...)

# ✅ 팀 초대 시리얼라이저
class InvitationSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)  # 초대받은 사용자 정보 포함

    class Meta:
        model = Invitation
        fields = ['id', 'user', 'status']  # 초대 ID, 유저 정보, 상태 ('pending', 'accepted', ...)

# ✅ 팀 시리얼라이저 - 상세 보기용 (리더, 멤버, 신청/초대 내역까지 포함)
class TeamSerializer(serializers.ModelSerializer):
    leader = SimpleUserSerializer(read_only=True)  # 팀장 정보
    members = SimpleUserSerializer(many=True, read_only=True)  # 팀원들
    applications = ApplicationSerializer(many=True, read_only=True, source='applications.all')  # 신청 목록
    invitations = InvitationSerializer(many=True, read_only=True, source='invitations.all')  # 초대 목록

    class Meta:
        model = Team
        fields = [
            'id',
            'leader',
            'intro',
            'tech_stack',
            'roles_needed',
            'domain',
            'max_members',
            'reward',
            'members',
            'applications',
            'invitations'
        ]

# ✅ 유저 검색/필터링용 시리얼라이저 (사용자 자체 정보)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'skills', 'mainRole', 'keywords', 'rating', 'participation']  # 실제 User 모델에 이 필드들이 있어야 함
