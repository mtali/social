from django.apps import AppConfig


# noinspection PyUnresolvedReferences
class ImagesConfig(AppConfig):
    name = 'images'

    def ready(self):
        import images.signals
