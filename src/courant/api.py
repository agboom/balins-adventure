from rest_framework import mixins, viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from rest_framework.routers import DefaultRouter

class CourantViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
  ):

  permission_classes = [IsAuthenticated]
  serializer_class = CourantSerializer

  def get_queryset(self):
    if self.request.user.has_perm('courant.view_courant'):
      return Courant.objects.all()
    else:
      return Courant.objects.filter(publish_date__lte=datetime.now())

  @detail_route(methods=["post"])
  def create_entry(self, request, pk):
    """ Create courant entry
        ---
        serializer: CourantEntrySerializer
    """
    serializer = CourantEntrySerializer(data=request.data)
    if serializer.is_valid():
      entry = serializer.instance
      entry.user = request.profiel
      entry.courant_id = pk
      entry.date_created = datetime.now()
      entry.date_modified = datetime.now()
      entry.save()
      return Response(CourantEntrySerializer(instance=entry))

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourantEntryViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
  ):

  permission_classes = [IsAuthenticated]
  serializer_class = CourantEntrySerializer

  def get_queryset(self):
    if self.request.user.has_perm('courant.view_courant'):
      return CourantEntry.objects.all()
    else:
      # limited access for regular users, only published or owned entries
      return CourantEntry.objects.filter(
        Q(courant__publish_date__lte=datetime.now()) | Q(user__pk=self.request.user.pk)
      )


  queryset = CourantEntry.objects.all()

router = DefaultRouter()
router.register('courant', CourantViewSet, base_name='courant')
router.register('courant/entry', CourantEntryViewSet, base_name='courantentry')
urls = router.urls
