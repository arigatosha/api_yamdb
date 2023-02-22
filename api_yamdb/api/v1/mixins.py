from rest_framework import mixins, viewsets


class CreateListDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    class Meta:
        abstract = True
