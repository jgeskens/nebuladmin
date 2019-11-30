from io import BytesIO, StringIO

from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils.text import slugify

from nebula.models import Member

import paramiko


@staff_member_required
def generate_config_file(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    context = {'network': member.network, 'member': member}
    response = render(request, 'nebula/config.yaml', context)
    filename = slugify(member.name)
    response['Content-Disposition'] = f'attachment; filename="{filename}.yaml"'
    return response


def deployment_action_view(member_id, template_attr, stream=True):
    member = get_object_or_404(Member, pk=member_id)
    context = {'network': member.network, 'member': member}
    if (deployment := member.get_deployment()) is None:
        raise Http404
    if (ssh := member.ssh_credentials) is None:
        raise Http404

    template_file = getattr(deployment, template_attr)
    script = render_to_string(template_name=template_file, context=context).replace('\r', '')

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    pkey = paramiko.RSAKey.from_private_key(StringIO(key)) if (key := ssh.key) else None
    client.connect(ssh.host, port=ssh.port, username=ssh.user, password=ssh.password or None, pkey=pkey)

    sftp = client.open_sftp()

    with sftp.file('/tmp/join_script', 'wb') as fh:
        fh.write(script.encode('utf-8'))

    if ssh.user == 'root':
        stdin, stdout, stderr = client.exec_command(
            f'chmod +x /tmp/join_script\n'
            f'nohup /tmp/join_script </dev/null >/tmp/nebula_deploy_log 2>&1 &\n' +
            f'tail -f /tmp/nebula_deploy_log' if stream else ''
        )
    else:
        stdin, stdout, stderr = client.exec_command(
            f'chmod +x /tmp/join_script\n'
            f'echo \'{ssh.password}\' | nohup sudo -S /tmp/join_script >/tmp/nebula_deploy_log 2>&1 &\n' +
            f'tail -f /tmp/nebula_deploy_log' if stream else ''
        )
    def read_stdout():
        line = stdout.readline()
        while line and line != 'OK\n':
            yield line
            line = stdout.readline()
        if line == 'OK\n':
            yield line

    if stream:
        return StreamingHttpResponse(read_stdout(), content_type='text/plain')
    else:
        return HttpResponse('OK')


@staff_member_required
def join_member(request, member_id):
    return deployment_action_view(member_id, 'join_template')


@staff_member_required
def leave_member(request, member_id):
    return deployment_action_view(member_id, 'leave_template')


@staff_member_required
def update_member(request, member_id):
    return deployment_action_view(member_id, 'update_template')
