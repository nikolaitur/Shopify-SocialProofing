# Populate ModalTextSettings table with default values.
import sys
import os
import django

sys.path.append("..")  # here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from app.models import ModalTextSettings

prompts = [
    'Dummy value',
    'Dummy value',
    'Dummy value',
    'Dummy value',
    'Dummy value',
]

for x, prompt in enumerate(prompts):
    ModalTextSettings.objects.update_or_create(modal_text_id=x,
                                               defaults={'modal_text_field': prompt,
                                                         'modal_text_id': x})
