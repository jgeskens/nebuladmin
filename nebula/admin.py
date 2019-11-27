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
    readonly_fields = ('generate_config',)

    def generate_config(self, member):
        url = reverse('generate_config', kwargs=dict(member_id=member.pk))
        return mark_safe(f'<a href="{url}">Generate config</a>')


@admin.register(models.Network)
class NetworkAdmin(admin.ModelAdmin):
    inlines = (MemberInline,)
    readonly_fields = ('ca_crt', 'ca_key')


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    readonly_fields = ('member_crt', 'member_key')
