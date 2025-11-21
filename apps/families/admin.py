from django.contrib import admin
from .models import Family, FamilyMembership, JoinRequest, Invitation

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'owner', 'created_at')
    search_fields = ('name', 'code', 'owner__email')

@admin.register(FamilyMembership)
class FamilyMembershipAdmin(admin.ModelAdmin):
    list_display = ('family', 'user', 'role', 'joined_at')
    list_filter = ('role',)

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('family', 'user', 'created_at', 'status')
    list_filter = ('status',)

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient_email', 'sender', 'accepted', 'created_at']
    search_fields = ('email', )
