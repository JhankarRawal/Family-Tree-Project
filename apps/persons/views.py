from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Person
from .mixins import FamilyPermissionMixin
from django.views.generic import CreateView,DetailView,UpdateView,DeleteView,ListView
from django.urls import reverse,reverse_lazy
from .forms import PersonForm
from apps.activitylog.utils import log_activity

class PersonListView(FamilyPermissionMixin, ListView):
    model = Person
    template_name = "persons/person_list.html"
    paginate_by = 50
    context_object_name = "people"
    allowed_roles = ["owner", "admin", "editor", "viewer"]

    def get_queryset(self):
        qs = Person.objects.filter(family=self.family).order_by("last_name")

        q = self.request.GET.get("q")
        gender = self.request.GET.get("gender")
        living = self.request.GET.get("living")

        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(birth_place__icontains=q)
            )

        if gender in ("male", "female", "other"):
            qs = qs.filter(gender=gender)

        if living in ("yes", "no"):
            qs = qs.filter(is_living=(living == "yes"))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family = context["family"]

        membership = self.request.user.family_memberships.filter(family=family).first()

        context["user_role"] = membership.role if membership else None
        return context
    
class PersonCreateView(FamilyPermissionMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "persons/person_form.html"
    allowed_roles = ["owner", "admin", "editor"]

    def form_valid(self, form):
        form.instance.family = self.family
        return super().form_valid(form)
    def form_valid(self, form):
        person = form.save()
        log_activity(
            family=person.family,
            user=self.request.user,
            action_type="create",
            target_type="person",
            target_id=person.id,
            description=f"Created person {person.first_name} {person.last_name}"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("persons:person_detail", kwargs={
            "pk": self.family.pk,
            "person_id": self.object.pk
        })
    
class PersonDetailView(FamilyPermissionMixin, DetailView):
    model = Person
    template_name = "persons/person_detail.html"
    pk_url_kwarg = "person_id"
    context_object_name = "person"
    allowed_roles = ["owner", "admin", "editor", "member"]

    def get_queryset(self):
        return Person.objects.filter(family=self.family)
    

class PersonUpdateView(FamilyPermissionMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "persons/person_form.html"
    pk_url_kwarg = "person_id"
    allowed_roles = ["owner", "admin", "editor"]

    def get_queryset(self):
        return Person.objects.filter(family=self.family)
    def form_valid(self, form):
        person = form.save()

        log_activity(
            family=person.family,
            user=self.request.user,
            action_type="update",
            target_type="person",
            target_id=person.id,
            description=f"Updated person {person.first_name} {person.last_name}"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("persons:person_detail", kwargs={
            "pk": self.family.pk,
            "person_id": self.object.pk
        })
    
class PersonDeleteView(FamilyPermissionMixin, DeleteView):
    model = Person
    template_name = "persons/person_confirm_delete.html"
    pk_url_kwarg = "person_id"
    allowed_roles = ["owner", "admin", "editor"]

    def get_queryset(self):
        return Person.objects.filter(family=self.family)
    def post(self, request, family_id, person_id):
        person = get_object_or_404(Person, id=person_id)
        person.delete()

        log_activity(
            family=person.family,
            user=request.user,
            action_type="delete",
            target_type="person",
            target_id=person_id,
            description=f"Deleted person {person.first_name} {person.last_name}"
        )

        return redirect("families:family_detail", pk=family_id)

    def get_success_url(self):
        return reverse_lazy("persons:list", kwargs={"pk": self.family.pk})
    
