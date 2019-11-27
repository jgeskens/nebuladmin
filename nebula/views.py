from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify

from nebula.models import Member


@staff_member_required
def generate_config_file(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    context = {'network': member.network, 'member': member}
    response = render(request, 'nebula/config.yaml', context)
    filename = slugify(member.name)
    response['Content-Disposition'] = f'attachment; filename="{filename}.yaml"'
    return response
