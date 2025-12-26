def apply_person_filters(queryset, filters):
    if gender := filters.get("gender"):
        queryset = queryset.filter(gender=gender)

    if alive := filters.get("alive"):
        if alive.lower() in ["true", "false"]:
            queryset = queryset.filter(is_alive=(alive.lower() == "true"))

    if start_year := filters.get("start_year"):
        if end_year := filters.get("end_year"):
            queryset = queryset.filter(birth_year__range=(start_year, end_year))

    return queryset
