from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
from import_export.admin import ExportActionMixin
from import_export import fields, resources


# Register your models here.
class CustomUserAdmin(ExportActionMixin, UserAdmin):
    list_display = ['first_name', 'last_name', 'username', 'email', 'wallet', 'phone', 'status']

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Other Personal info',
            {
                'fields': (
                    'phone', 'wallet', 'status'
                )
            }
        )
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'password1', 'password2', 'wallet')
        }),)
    

class IShareBundleTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'bundle_number', 'offer', 'reference', 'transaction_status', 'transaction_date']
    search_fields = ['reference', 'bundle_number']
    

class MTNTransactionResource(resources.ModelResource):
    bundle_number_with_zero = fields.Field(column_name='Bundle Number with Zero')

    class Meta:
        model = models.MTNTransaction
        fields = ['user', 'bundle_number_with_zero', 'offer', 'reference', 'transaction_status', 'transaction_date']

    def dehydrate_bundle_number_with_zero(self, obj):
        # Assuming 'bundle_number' is the field that needs modification
        return f'0{obj.bundle_number}' if obj.bundle_number and len(str(obj.bundle_number)) == 9 else obj.bundle_number

class MTNTransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['user', 'bundle_number', 'offer', 'reference', 'transaction_status', 'transaction_date']
    search_fields = ['reference', 'bundle_number']
    resource_class = MTNTransactionResource


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'reference', 'transaction_date', 'amount']


class TopUpRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'reference', 'amount', 'date', 'status']


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.IShareBundleTransaction, IShareBundleTransactionAdmin)
admin.site.register(models.MTNTransaction, MTNTransactionAdmin)
admin.site.register(models.IshareBundlePrice)
admin.site.register(models.MTNBundlePrice)
admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.AdminInfo)
admin.site.register(models.TopUpRequest, TopUpRequestAdmin)
admin.site.register(models.AgentIshareBundlePrice)
admin.site.register(models.AgentMTNBundlePrice)


