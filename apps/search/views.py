from django.views.generic import TemplateView, View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from apps.persons.models import Person
from apps.families.models import Family
from .services import apply_person_filters
from .algorithms import bfs_relationship_path, dfs_ancestors, dfs_descendants
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class PersonSearchView(LoginRequiredMixin, ListView):
    model = Person
    template_name = 'search/person_search.html'
    context_object_name = 'members'

    def get_queryset(self):
        # Ensure the logged-in user belongs to the family
        self.family = get_object_or_404(
            Family,
            id=self.kwargs['family_id'],
            memberships__user=self.request.user  # checks that user belongs to family
        )

        # Get all persons in this family
        queryset = Person.objects.filter(family=self.family)

        # Apply search query
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(first_name__icontains=query)  # or name field
        return queryset



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['family'] = self.family
        context['query'] = self.request.GET.get('q', '')
        return context


class PersonFilterView(TemplateView):
    template_name = "search/filter_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family_id = self.kwargs["family_id"]
        persons = Person.objects.filter(family_id=family_id)
        persons = apply_person_filters(persons, self.request.GET)
        context["persons"] = persons
        return context


class PersonAutocompleteView(View):
    def get(self, request, family_id, *args, **kwargs):
        term = request.GET.get("term", "")
        persons = Person.objects.filter(family_id=family_id, first_name__icontains=term)[:10]

        results = [{"id": p.id, "label": str(p), "value": str(p)} for p in persons]
        return JsonResponse(results, safe=False)
class RelationshipPathView(TemplateView):
    template_name = "search/relationship_path.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_id = self.kwargs["start_id"]
        end_id = self.kwargs["end_id"]

        start = get_object_or_404(Person, id=start_id)
        end = get_object_or_404(Person, id=end_id)

        path = bfs_relationship_path(start, end)
        context.update({"path": path})
        return context
class AncestorsView(TemplateView):
    template_name = "search/ancestors_descendants.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = get_object_or_404(Person, id=self.kwargs["person_id"])
        context["ancestors"] = dfs_ancestors(person)
        context["descendants"] = dfs_descendants(person)
        context["person"] = person
        return context
