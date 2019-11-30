from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import models


admin.site.register(models.StaticHost)


class MemberInline(admin.TabularInline):
    model = models.Member
    exclude = ('member_crt', 'member_key')
    extra = 0
    show_change_link = True
    readonly_fields = ('actions',)

    def actions(self, member):
        if member.pk is None:
            return ''
        config_url = reverse('generate_config', kwargs=dict(member_id=member.pk))
        join_url = reverse('join_member', kwargs=dict(member_id=member.pk))
        leave_url = reverse('leave_member', kwargs=dict(member_id=member.pk))
        update_url = reverse('update_member', kwargs=dict(member_id=member.pk))
        return mark_safe(f'<a href="{config_url}">Generate config</a><br>'
                         f'<a href="{join_url}">Join</a>&nbsp;'
                         f'<a href="{update_url}">Update</a>&nbsp;'
                         f'<a href="{leave_url}">Leave</a>')


@admin.register(models.Network)
class NetworkAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    readonly_fields = ('ca_crt', 'ca_key')


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    readonly_fields = ('member_crt', 'member_key')

    def reset_pki(self, request, queryset):
        for member in queryset.all():
            member.member_key = ''
            member.member_crt = ''
            member.full_clean()
            member.save()

    actions = (reset_pki,)


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
