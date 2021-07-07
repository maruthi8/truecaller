from rest_framework import routers

from api.views import UserViewSet, ContactViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register("user", UserViewSet, basename="users")
router.register("contact", ContactViewSet, basename="contacts")

urlpatterns = router.urls
