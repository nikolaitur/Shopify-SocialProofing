# Populate ModalTextSettings table with default values.

from app.models import ModalTextSettings

prompts = [
    '%s customers have bought this item in the last %s days.',
    '%s customers have viewed this item in the last %s days.',
]

for x, prompt in enumerate(prompts):
    ModalTextSettings.objects.update_or_create(modal_text_id=x,
                                               defaults={'modal_text_field': prompt,
                                                         'modal_text_id': x})
