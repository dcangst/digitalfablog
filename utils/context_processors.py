"""
    custom context processors
"""


def global_variables(request):
    is_labmanager = request.user.groups.filter(name="labmanager").exists()
    is_staff = request.user.is_staff

    return {'is_labmanager': is_labmanager,
            'is_staff': is_staff}
