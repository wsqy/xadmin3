"""
Form Widget classes specific to the Django admin site.
"""
from itertools import chain
from django import forms
try:
    from django.forms.widgets import ChoiceWidget as RadioChoiceInput
except:
    from django.forms.widgets import RadioFieldRenderer, RadioChoiceInput
from django.utils.encoding import force_str

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.translation import gettext as _

from .util import vendor


class AdminDateWidget(forms.DateInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'datepicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'date-field form-control', 'size': '10'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminDateWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super(AdminDateWidget, self).render(name, value, attrs, renderer)
        return mark_safe('<div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Today')))


class AdminTimeWidget(forms.TimeInput):

    @property
    def media(self):
        return vendor('datepicker.js', 'clockpicker.js', 'clockpicker.css', 'xadmin.widget.datetime.js')

    def __init__(self, attrs=None, format=None):
        final_attrs = {'class': 'time-field form-control', 'size': '8'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTimeWidget, self).__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = super(AdminTimeWidget, self).render(name, value, attrs, renderer)
        return mark_safe('<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>' % (input_html, _(u'Now')))


class AdminSelectWidget(forms.Select):

    @property
    def media(self):
        return vendor('select.js', 'select.css', 'xadmin.widget.select.js')


class AdminSplitDateTime(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """

    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def render(self, name, value, attrs=None, renderer=None):
        input_html = [ht for ht in super(AdminSplitDateTime, self).render(name, value, attrs, renderer).replace('><input', '>\n<input').split('\n') if ht != '']
        # return input_html
        return mark_safe('<div class="datetime clearfix"><div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>'
                         '<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div></div>' % (input_html[0], _(u'Today'), input_html[1], _(u'Now')))

    def format_output(self, rendered_widgets):
        return mark_safe(u'<div class="datetime clearfix">%s%s</div>' %
                         (rendered_widgets[0], rendered_widgets[1]))


class AdminRadioSelect(forms.RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        final_attrs['class'] = final_attrs.get('class', '').replace('form-control', '')
        output = []
        str_values = set([force_str(v) for v in ([value] if not isinstance(value, (list, tuple)) else value)])
        _choices = self.choices
        if callable(_choices):
            _choices = _choices()
        if callable(_choices) or not isinstance(_choices, (list, tuple)):
            _choices = list(_choices) if _choices else []
        for i, (option_value, option_label) in enumerate(_choices):
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = ' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            option_value = force_str(option_value)
            checked = ' checked' if option_value in str_values else ''
            inline = final_attrs.pop('inline', False) if i == 0 else final_attrs.get('inline', False)
            input_attrs = final_attrs.copy()
            input_attrs['type'] = 'radio'
            input_attrs['value'] = option_value
            if checked:
                input_attrs['checked'] = 'checked'
            attr_str = ' '.join(['%s="%s"' % (k, conditional_escape(v)) for k, v in input_attrs.items()])
            input_html = '<input %s/>' % attr_str
            option_label = conditional_escape(force_str(option_label))
            if inline:
                output.append('<label%s class="radio-inline">%s %s</label>' % (label_for, input_html, option_label))
            else:
                output.append('<div class="radio"><label%s>%s %s</label></div>' % (label_for, input_html, option_label))
        return mark_safe('\n'.join(output))


class AdminCheckboxSelect(forms.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        output = []
        # Normalize to strings
        str_values = set([force_str(v) for v in value])
        _choices = self.choices
        if callable(_choices):
            _choices = _choices()
        if callable(_choices) or not isinstance(_choices, (list, tuple)):
            _choices = list(_choices) if _choices else []
        # In Django 4.2+, ChoiceWidget.options is a method, not a data attribute
        _opts = getattr(self, 'options', [])
        if callable(_opts):
            _opts = []
        for i, (option_value, option_label) in enumerate(chain(_choices, _opts)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = ' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_str(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_str(option_label))

            if final_attrs.get('inline', False):
                output.append('<label%s class="checkbox-inline">%s %s</label>' % (label_for, rendered_cb, option_label))
            else:
                output.append('<div class="checkbox"><label%s>%s %s</label></div>' % (label_for, rendered_cb, option_label))
        return mark_safe('\n'.join(output))


class AdminSelectMultiple(forms.SelectMultiple):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'select-multi'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminSelectMultiple, self).__init__(attrs=final_attrs)


class AdminFileWidget(forms.ClearableFileInput):
    template_with_initial = (u'<p class="file-upload">%s</p>'
                             % forms.ClearableFileInput.initial_text)
    template_with_clear = (u'<span class="clearable-file-input">%s</span>'
                           % forms.ClearableFileInput.clear_checkbox_label)


class AdminTextareaWidget(forms.Textarea):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'textarea-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextareaWidget, self).__init__(attrs=final_attrs)


class AdminTextInputWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'text-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminTextInputWidget, self).__init__(attrs=final_attrs)


class AdminURLFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'url-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminURLFieldWidget, self).__init__(attrs=final_attrs)


class AdminIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminIntegerFieldWidget, self).__init__(attrs=final_attrs)


class AdminCommaSeparatedIntegerFieldWidget(forms.TextInput):

    def __init__(self, attrs=None):
        final_attrs = {'class': 'sep-int-field'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminCommaSeparatedIntegerFieldWidget,
              self).__init__(attrs=final_attrs)
