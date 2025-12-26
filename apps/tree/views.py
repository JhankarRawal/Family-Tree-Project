from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from apps.persons.models import Person
from .services import build_tree

class FamilyTreeView(TemplateView):
    template_name = "tree/tree_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family_id = self.kwargs["family_id"]
        root = Person.objects.filter(family_id=family_id).first()
        context["family_id"] = family_id
        context["root_person"] = root
        return context


class CenteredTreeView(FamilyTreeView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["root_person"] = get_object_or_404(
            Person, id=self.kwargs["person_id"]
        )
        return context


class TreeDataAPIView(View):
    def get(self, request, family_id, person_id):
        show_deceased = request.GET.get("show_deceased", "true") == "true"
        person = get_object_or_404(Person, id=person_id, family_id=family_id)
        data = build_tree(person, show_deceased=show_deceased)
        return JsonResponse(data)
