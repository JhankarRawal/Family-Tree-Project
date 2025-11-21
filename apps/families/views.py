from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from apps.persons.models import Person
from .models import Family, FamilyMembership, Invitation, JoinRequest
from .forms import FamilyForm, JoinByCodeForm, InvitationForm
from .utils import generate_family_code
from django.utils import timezone
from django.utils.crypto import get_random_string

class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'families/family_list.html'
    context_object_name = 'families'

    def get_queryset(self):
        return Family.objects.filter(
            memberships__user=self.request.user
        ).prefetch_related('memberships__user').distinct().order_by('name')
    
class FamilyCreateView(LoginRequiredMixin, CreateView):
    model = Family
    form_class = FamilyForm
    template_name = 'families/family_form.html'
    def form_valid(self, form):
        family = form.save(commit=False)
        family.owner = self.request.user
        family.code = generate_family_code()
        family.save()
        # create membership as owner
        FamilyMembership.objects.create(family=family, user=self.request.user, role='owner')
        messages.success(self.request, 'Family created.')
        return redirect('families:detail', pk=family.pk)

class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'families/family_detail.html'


    def get(self, request, *args, **kwargs):
        family = self.get_object()
        # security: only members can view
        if not family.memberships.filter(user=request.user).exists():
            messages.error(request, 'You are not a member of this family.')
            return redirect('families:list')
        return super().get(request, *args, **kwargs)



class FamilyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Family
    form_class = FamilyForm
    template_name = 'families/family_form.html'

    def test_func(self):
        family = self.get_object()
        # only owner or admin can update
        membership = family.memberships.filter(user=self.request.user).first()
        return membership and membership.role in ('owner', 'admin')
    def handle_no_permission(self):
        messages.error(self.request, 'Not permitted to edit family.')
        return redirect('families:detail', pk=self.get_object().pk)
    
class FamilyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Family
    template_name = 'families/family_confirm_delete.html'
    success_url = reverse_lazy('families:list')
    def test_func(self):
        family = self.get_object()
        membership = family.memberships.filter(user=self.request.user).first()
        return membership and membership.role == 'owner'
    
class MembersManageView(LoginRequiredMixin, TemplateView):
    template_name = 'families/manage_members.html'

    def dispatch(self, request, *args, **kwargs):
        self.family = get_object_or_404(Family, pk=kwargs['pk'])
        if not self.family.memberships.filter(user=request.user).exists():
            messages.error(request, 'You are not a member of this family.')
            return redirect('families:list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['family'] = self.family
        ctx['memberships'] = self.family.memberships.select_related('user')
        ctx['join_requests'] = self.family.join_requests.filter(status='pending').select_related('user')
        # Precompute owner/admin users for template
        ctx['owner_admin_users'] = self.family.memberships.filter(
            role__in=['owner', 'admin']
        ).values_list('user_id', flat=True)
        ctx['owner_user'] = self.family.memberships.filter(role='owner').first().user
        return ctx
    
    # Actions: approve/reject join, remove member, change role
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator


class ApproveJoinRequestView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk, jr_pk):
        # Get the family and join request
        family = get_object_or_404(Family, pk=pk)
        jr = get_object_or_404(JoinRequest, pk=jr_pk, family=family)

        # Only owner/admin can approve
        current_membership = family.memberships.filter(user=request.user).first()
        if not current_membership or current_membership.role not in ('owner', 'admin'):
            messages.error(request, "Permission denied.")
            return redirect('families:members', pk=family.pk)

        # Check if user is already a member to avoid IntegrityError
        if FamilyMembership.objects.filter(family=family, user=jr.user).exists():
            messages.warning(request, f"{jr.user.get_full_name()} is already a member.")
        else:
            # Approve the join request
            jr.status = 'approved'
            jr.processed_by = request.user
            jr.processed_at = timezone.now()
            jr.save()

            # Add user as member
            FamilyMembership.objects.create(family=family, user=jr.user, role='member')

            # Notify user via email
            send_mail(
                subject=f'Join request approved for {family.name}',
                message=f'Your request to join {family.name} has been approved.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[jr.user.email],
                fail_silently=True,
            )

            messages.success(request, f"{jr.user.get_username()} has been added to the family.")

        # Delete the join request in any case to keep dashboard clean
        jr.delete()

        return redirect('families:members', pk=family.pk)


class RejectJoinRequestView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk, jr_pk):
        # Get the family and join request
        family = get_object_or_404(Family, pk=pk)
        jr = get_object_or_404(JoinRequest, pk=jr_pk, family=family)

        # Only owner/admin can reject
        current_membership = family.memberships.filter(user=request.user).first()
        if not current_membership or current_membership.role not in ('owner', 'admin'):
            messages.error(request, "Permission denied.")
            return redirect('families:members', pk=family.pk)

        # Mark the join request as rejected
        jr.status = 'rejected'
        jr.processed_by = request.user
        jr.processed_at = timezone.now()
        jr.save()

        # Notify user
        send_mail(
            subject=f'Join request rejected for {family.name}',
            message=f'Your request to join {family.name} has been rejected.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[jr.user.email],
            fail_silently=True,
        )

        # Optional: remove rejected request from dashboard
        # jr.delete()  # Uncomment if you want to remove it completely

        messages.info(request, f"{jr.user.get_full_name()}'s join request has been rejected.")
        return redirect('families:members', pk=family.pk)



class JoinByCodeView(LoginRequiredMixin, FormView):
    template_name = 'families/join_by_code.html'
    form_class = JoinByCodeForm
    success_url = '/families/list/'  # adjust as needed

    def form_valid(self, form):
        code = form.cleaned_data['code']
        message = form.cleaned_data.get('message', '')

        # Get the family by code
        family = get_object_or_404(Family, code=code)

        # Check if a join request already exists
        if JoinRequest.objects.filter(user=self.request.user, family=family,status='pending').exists():
            messages.warning(self.request, "You already sent a join request to this family.")
            return redirect(self.success_url)

        # Create the join request
        JoinRequest.objects.create(
            user=self.request.user,
            family=family,
            message=message
        )

        messages.success(self.request, "Join request sent successfully!")
        return redirect(self.success_url)
# adjust as needed

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context
    # template_name = 'families/join_by_code.html'
    # form_class = JoinRequestForm

    # def form_valid(self, form):
    #     code = form.cleaned_data['code']
    #     try:
    #         family = Family.objects.get(code=code)
    #         JoinRequest.objects.create(user=self.request.user, family=family)
    #         messages.success(self.request, "Join request sent!")
    #     except Family.DoesNotExist:
    #         messages.error(self.request, "Family with this code does not exist.")
    #         return self.form_invalid(form)
    #     return redirect('families:list')
    

@method_decorator(require_POST, name='dispatch')
class ChangeMemberRoleView(LoginRequiredMixin, FormView):
    """
    Change a family member's role.
    Only the owner can change roles.
    Owner role cannot be changed.
    """

    def post(self, request, pk, member_id):
        family = get_object_or_404(Family, pk=pk)
        membership = family.memberships.filter(user=request.user).first()
        target = get_object_or_404(FamilyMembership, pk=member_id, family=family)

        # Only owner can change roles
        if not membership or membership.role != 'owner':
            messages.error(request, 'Permission denied: only the owner can change roles.')
            return redirect('families:members', pk=family.pk)

        # Cannot change owner's role
        if target.role == 'owner':
            messages.error(request, 'Cannot change the role of the owner.')
            return redirect('families:members', pk=family.pk)

        # Get new role from POST data
        new_role = request.POST.get('role')
        if new_role not in ['admin', 'member']:
            messages.error(request, 'Invalid role selected.')
            return redirect('families:members', pk=family.pk)

        target.role = new_role
        target.save()
        messages.success(request, f"{target.user.username}'s role has been changed to {new_role}.")
        return redirect('families:members', pk=family.pk)
    

def invite_member(request, pk):
    family = get_object_or_404(Family, pk=pk)
    
    # Check if the user is allowed to invite (owner/admin)
    membership = family.memberships.filter(user=request.user).first()
    if not membership or membership.role not in ('owner', 'admin'):
        messages.error(request, "You do not have permission to send invitations.")
        return redirect('families:members', pk=family.pk)

    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.family = family
            invitation.sender = request.user
            # generate a unique token
            invitation.token = get_random_string(64)
            invitation.save()
            # Optional: send email
            send_mail(
                subject=f"Invitation to join {family.name}",
                message=f"You have been invited to join the family {family.name}. Use this token: {invitation.token}\n\nMessage: {invitation.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitation.recipient_email],
                fail_silently=True
            )
            
            messages.success(request, "Invitation sent successfully!")
            return redirect('families:members', pk=family.pk)
    else:
        form = InvitationForm()
    
    return render(request, 'families/invite_form.html', {'form': form, 'family': family})

class AcceptInviteView(FormView):
    def get(self, request):
        token = request.GET.get('token')
        invitation = get_object_or_404(Invitation, token=token)
        # You can handle logic here: mark accepted, add user to family, etc.
        invitation.accepted = True
        invitation.save()
        messages.success(request, f"You have joined {invitation.family.name}")
        return redirect('dashboard')  # or some page      return redirect('families:members', pk=family.pk)
    # def family_tree_view(request, pk):
    #     family = get_object_or_404(Family, pk=pk)
    # # Pass the family object to template
    #     return render(request, 'families/family_tree.html', {'family': family})

class RemoveMemberView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk, member_id):
        # Get the family
        family = get_object_or_404(Family, pk=pk)

        # Get the membership to remove
        membership_to_remove = get_object_or_404(
            FamilyMembership,
            family=family,
            user_id=member_id
        )
        # Only owner/admin can remove, cannot remove owner
        current_membership = family.memberships.filter(user=request.user).first()
        if not current_membership or current_membership.role not in ('owner', 'admin'):
            messages.error(request, "Permission denied.")
            return redirect('families:members', pk=family.pk)

        if membership_to_remove.role == 'owner':
            messages.error(request, "You cannot remove the owner.")
            return redirect('families:members', pk=family.pk)

        # Remove the membership
        membership_to_remove.delete()

        # ✅ Delete any pending join requests (approved=None) for this user in the same family
        JoinRequest.objects.filter(
            family=family,
            user_id=member_id,
            status='approved'
        ).update(status='cancelled')

        messages.success(
            request,
            f"{membership_to_remove.user.get_full_name()} has been removed from the family."
        )

        return redirect('families:members', pk=family.pk)
    

