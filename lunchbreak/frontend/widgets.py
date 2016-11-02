from datetime import datetime

from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from lunch.models import Period


class ReceiptField(widgets.Widget):

    supports_microseconds = False
    name_weekday = '-weekday'
    name_time = '-time'

    def __init__(self, store, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store = store

    def render(self, name, value, attrs=None):
        if value is not None:
            value = value.in_timezone(self.store.timezone)
        return mark_safe(
            render_to_string(
                template_name='widgets/receipt_field.html',
                context={
                    'name_weekday': name + self.name_weekday,
                    'name_time': name + self.name_time,
                    'value': value,
                    'attrs': attrs,
                    'store': self.store
                }
            )
        )

    def value_from_datadict(self, data, files, name):
        try:
            time = datetime.strptime(
                data.get(name + self.name_time),
                '%H:%M'
            ).time()
            pend = Period.weekday_as_datetime(
                weekday=int(data.get(name + self.name_weekday)),
                time=time,
                store=self.store
            )
            return pend
        except TypeError:
            return None
