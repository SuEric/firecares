from django.conf import settings
from django.core.cache import cache
from firecares.firestation.models import FireDepartment, Max, Min


def global_settings(request):
    """
    Expose various settings
    """
    return {
        'global_settings': {
            'google_analytics_tracking_id': settings.GOOGLE_ANALYTICS_TRACKING_ID,
            'SSO_LOGIN_URL': settings.SSO_LOGIN_URL
        }
    }


def fire_department_search(request):
    """
    Required context variables for fire department search.
    """
    context = cache.get('fire_department_search_context')
    if context:
        return context

    score_metrics = FireDepartment.objects.filter(archived=False).aggregate(
        Max('dist_model_score'),
        Min('dist_model_score'),
        Max('population'),
        Min('population'),
    )

    context = {
        'dist_max': score_metrics['dist_model_score__max'],
        'dist_min': score_metrics['dist_model_score__min'],
        'population_max': score_metrics['population__max'] or 0,
        'population_min': score_metrics['population__min'] or 0,
    }

    cache.set('fire_department_search_context', context, 60 * 60 * 24)

    return context
