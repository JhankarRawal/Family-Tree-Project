from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Person
from .mixins import FamilyPermissionMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.urls import reverse, reverse_lazy
from .forms import PersonForm
from apps.activitylog.utils import log_activity
from apps.families.models import Family

class PersonListView(FamilyPermissionMixin, ListView):
    model = Person
    template_name = "persons/person_list.html"
    paginate_by = 50
    context_object_name = "people"
    allowed_roles = ["owner","member", "admin",  "viewer"]

    def get_family(self):
        return get_object_or_404(Family, pk=self.kwargs["family_id"])

    def get_queryset(self):
        self.family = self.get_family()
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
        self.family = self.get_family()
        context["family"] = self.family

        membership = self.request.user.family_memberships.filter(family=self.family).first()
        context["user_role"] = membership.role if membership else None
        return context


class PersonCreateView(FamilyPermissionMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "persons/person_form.html"
    allowed_roles = ["owner", "admin"]

    def get_family(self):
        return get_object_or_404(Family, pk=self.kwargs["family_id"])

    def form_valid(self, form):
        self.family = self.get_family()
        form.instance.family = self.family
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
        return reverse("families:persons:person_detail", kwargs={
            "family_id": self.object.family_id,
            "person_id": self.object.pk
        })


class PersonDetailView(FamilyPermissionMixin, DetailView):
    model = Person
    template_name = "persons/person_detail.html"
    pk_url_kwarg = "person_id"
    context_object_name = "person"
    allowed_roles = ["owner", "admin", "member", "viewer"]

    def get_family(self):
        return get_object_or_404(Family, pk=self.kwargs["family_id"])

    def get_queryset(self):
        self.family = self.get_family()
        return Person.objects.filter(family=self.family)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["family"] = self.family
        return context


class PersonUpdateView(FamilyPermissionMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "persons/person_form.html"
    pk_url_kwarg = "person_id"
    allowed_roles = ["owner", "admin"]

    def get_family(self):
        return get_object_or_404(Family, pk=self.kwargs["family_id"])

    def get_queryset(self):
        self.family = self.get_family()
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
        return reverse("families:persons:person_detail", kwargs={
            "family_id": self.family.pk,
            "person_id": self.object.pk
        })


class PersonDeleteView(FamilyPermissionMixin, DeleteView):
    model = Person
    pk_url_kwarg = "person_id"
    allowed_roles = ["owner", "admin"]

    def get_family(self):
        return get_object_or_404(Family, pk=self.kwargs["family_id"])

    def get_queryset(self):
        self.family = self.get_family()
        return Person.objects.filter(family=self.family)

    def post(self, request, *args, **kwargs):
        self.family = self.get_family()
        person = get_object_or_404(Person, pk=self.kwargs["person_id"], family=self.family)

        log_activity(
            family=self.family,
            user=request.user,
            action_type="delete",
            target_type="person",
            target_id=person.id,
            description=f"Deleted person {person.first_name} {person.last_name}"
        )
        person.delete()
        return redirect("families:persons:list", family_id=self.family.pk)
