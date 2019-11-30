from django import forms
from django.contrib import admin
from django.http import Http404
from django.urls import reverse
from django.utils.safestring import mark_safe

from nebula.views import deployment_action_view
from . import models


admin.site.register(models.StaticHost)


def _member_actions(member):
    if member.pk is None:
        return ''
    config_url = reverse('generate_config', kwargs=dict(member_id=member.pk))
    join_url = reverse('join_member', kwargs=dict(member_id=member.pk))
    leave_url = reverse('leave_member', kwargs=dict(member_id=member.pk))
    update_url = reverse('update_member', kwargs=dict(member_id=member.pk))
    return mark_safe(f'<a href="{config_url}">Generate config</a><br>'
                     f'<a target="_blank" href="{join_url}">Join</a>&nbsp;'
                     f'<a target="_blank" href="{update_url}">Update</a>&nbsp;'
                     f'<a target="_blank" href="{leave_url}">Leave</a>')


class MemberInline(admin.TabularInline):
    model = models.Member
    exclude = ('member_crt', 'member_key', 'nebula_port', 'deployment', 'ssh_credentials', 'static_host')
    extra = 0
    show_change_link = True
    readonly_fields = ('name', 'address', 'is_lighthouse', 'expiry_date', 'actions',)

    def actions(self, member):
        return _member_actions(member)


@admin.register(models.Network)
class NetworkAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    readonly_fields = ('ca_crt', 'ca_key')


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_lighthouse', 'expiry_date', 'static_host', 'member_actions')
    list_filter = ('network', 'is_lighthouse',)
    readonly_fields = ('member_crt', 'member_key', 'member_actions')

    def member_actions(self, member):
        return _member_actions(member)

    def reset_pki(self, request, queryset):
        for member in queryset.all():
            member.member_key = ''
            member.member_crt = ''
            member.full_clean()
            member.save()

    def join(self, request, queryset):
        for member in queryset.all():
            try:
                deployment_action_view(member.pk, 'join_template', stream=False)
            except Http404:
                pass

    def leave(self, request, queryset):
        for member in queryset.all():
            try:
                deployment_action_view(member.pk, 'leave_template', stream=False)
            except Http404:
                pass

    def update(self, request, queryset):
        for member in queryset.all():
            try:
                deployment_action_view(member.pk, 'update_template', stream=False)
            except Http404:
                pass

    actions = (reset_pki, join, leave, update)


class SSHCredentialsAdminForm(forms.ModelForm):
    class Meta:
        model = models.SSHCredentials
        widgets = {'password': forms.PasswordInput()}
        fields = '__all__'


@admin.register(models.SSHCredentials)
class SSHCredentialsAdmin(admin.ModelAdmin):
    form = SSHCredentialsAdminForm
    readonly_fields = ('view_password',)

    def view_password(self, credentials):
        return mark_safe(f'<span title="{credentials.password}">tooltip</span>')
