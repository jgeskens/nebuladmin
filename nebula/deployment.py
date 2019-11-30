from typing import NamedTuple


class NebulaDeployment(NamedTuple):
    name: str
    slug: str
    join_template: str
    update_template: str
    leave_template: str


deployments = [
    NebulaDeployment(
        name='Ubuntu runit amd64',
        slug='amd64_ubuntu_runit',
        join_template='nebula/join_amd64_ubuntu_runit.sh',
        update_template='nebula/update_amd64_ubuntu_runit.sh',
        leave_template='nebula/leave_amd64_ubuntu_runit.sh'
    ),
    NebulaDeployment(
        name='Ubuntu systemd amd64',
        slug='amd64_ubuntu_systemd',
        join_template='nebula/join_amd64_ubuntu_systemd.sh',
        update_template='nebula/update_amd64_ubuntu_systemd.sh',
        leave_template='nebula/leave_amd64_ubuntu_systemd.sh'
    )
]

deployment_dict = {d.slug: d for d in deployments}

deployment_choices = [(d.slug, d.name) for d in deployments]
