"""
    custom context processors
"""


def global_variables(request):
    is_labmanager = request.user.has_perm('fablog.add_fablog')
    is_staff = request.user.is_staff

    return {'is_labmanager': is_labmanager,
            'is_staff': is_staff}
