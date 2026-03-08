from django import forms


class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "base/widgets/checkbox_select_multiple.html"


class SwitchSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "base/widgets/switch_select_multiple.html"
