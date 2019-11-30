from django.db import models
from django.utils.timezone import now

from nebula.backend import generate_network_credentials, generate_member_credentials
from nebula.deployment import deployment_choices, deployment_dict


class StaticHost(models.Model):
    name = models.CharField(max_length=255)
    address = models.GenericIPAddressField(protocol='ipv4')
    port = models.PositiveIntegerField(default=4242)

    def __str__(self):
        return f'{self.address}:{self.port} {self.name}'


class Network(models.Model):
    name = models.CharField(max_length=255)
    ca_crt = models.TextField()
    ca_key = models.TextField()
    address_prefix = models.GenericIPAddressField(protocol='ipv4')
    cidr_bits = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.address_prefix}/{self.cidr_bits} {self.name}'

    @property
    def static_members(self):
        return self.members.filter(static_host__isnull=False)

    @property
    def lighthouses(self):
        return self.members.filter(is_lighthouse=True)

    def full_clean(self, exclude=None, validate_unique=True):
        if not self.ca_crt or not self.ca_key:
            ca_data = generate_network_credentials(self.name, days=4 * 365)
            self.ca_crt = ca_data['crt']
            self.ca_key = ca_data['key']

        super().full_clean(exclude=exclude, validate_unique=validate_unique)


class SSHCredentials(models.Model):
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=22)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255, blank=True)
    key = models.TextField(blank=True)

    def __str__(self):
        portarg = '' if self.port == 22 else f' -p {self.port}'
        return f'{self.user}@{self.host}{portarg}'


class Member(models.Model):
    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name='members')

    name = models.CharField(max_length=255)
    address = models.GenericIPAddressField(protocol='ipv4')
    member_crt = models.TextField()
    member_key = models.TextField()
    expiry_date = models.DateField(blank=True, null=True)
    is_lighthouse = models.BooleanField(blank=True, default=False)
    static_host = models.ForeignKey(StaticHost, blank=True, null=True, on_delete=models.SET_NULL)
    nebula_port = models.PositiveIntegerField(default=4242)

    ssh_credentials = models.ForeignKey(SSHCredentials, blank=True, null=True, on_delete=models.SET_NULL)
    deployment = models.CharField(max_length=100, blank=True, choices=deployment_choices)

    class Meta:
        ordering = ('address',)

    def __str__(self):
        return f'{self.address} {self.name}'

    def full_clean(self, exclude=None, validate_unique=True):
        if not self.member_crt or not self.member_key:
            ca_data = generate_member_credentials(
                self.name,
                f'{self.address}/{self.network.cidr_bits}',
                self.network.ca_crt,
                self.network.ca_key,
                days=None if self.expiry_date is None else (self.expiry_date - now()).days
            )
            self.member_crt = ca_data['crt']
            self.member_key = ca_data['key']

        super().full_clean(exclude=exclude, validate_unique=validate_unique)

    def get_deployment(self):
        return deployment_dict.get(self.deployment)
