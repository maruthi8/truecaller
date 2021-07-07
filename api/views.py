from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import mixins

from api.models import User, UserProfile, Contact, UserContact
from api.serializers import UserSerializer, UserProfileSerializer, ContactSerializer


class UserViewSet(viewsets.ViewSet):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def register(self, request, *args, **kwargs):
        """Check if user profile already exists with phone number or not"""
        data = request.data
        user_serializer = UserSerializer(data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def deactivate(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        user = User.objects.get(pk=pk)
        user.is_active = False
        user.save()

        return Response(
            "You account has been successfully deactivated", status=status.HTTP_200_OK
        )


class UserProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class ContactViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.data("user"):
            raise ValidationError("User id is required to create contact and mapping")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        contact_data = serializer.data
        # create mapping for contact with user to identify for which user we loaded this contact.
        UserContact.objects.create(
            user_id=request.data.get("user"), contact_id=contact_data.get("id")
        )

    @action(methods=["GET"], detail=False)
    def search(self, request, *args, **kwargs):
        search_results = []

        name = request.GET.get("name")
        phone_number = request.GET.get("phone_number")

        contacts = Contact.objects.filter()
        if name:
            startwith_contacts = list(contacts.filter(name__startswith=name))
            contains_contacts = list(contacts.filter(name__icontains=name))
            startwith_contacts.extend(contains_contacts)
            search_results = startwith_contacts
        elif phone_number:
            user_profile = UserProfile.objects.filter(phone_number=phone_number)
            if user_profile.exists():
                user_contacts = user_profile.first().user.user_contacts.filter(
                    contact__number=phone_number
                )
                search_results = user_contacts.first().contact
            else:
                search_results = contacts.filter(number=phone_number)

        return Response(
            ContactSerializer(search_results, many=True).data, status=status.HTTP_200_OK
        )

    @action(methods=["patch"], detail=True)
    def is_spam(self, request, *args, **kwargs):
        contact = Contact.objects.get(pk=kwargs.get("pk"))
        contact.is_spam = request.data.get("is_spam")
        contact.save()

        return Response("Updated contact info", status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def bulk_create(self, request, *args, **kwargs):
        data = request.data
        if not data.get("user"):
            raise ValidationError("User is required to map contacts")
        for contact_data in data:
            contact_serializer = ContactSerializer(contact_data)
            contact_serializer.is_valid(raise_exception=True)
            contract_obj = contact_serializer.save()

            # create mapping for contact with user to identify for which user we loaded this contact.
            UserContact.objects.create(user_id=data.get("user"), contact=contract_obj)
        return Response("Loaded contact successfully", status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """List only contacts that are mapped to the user"""
        user = request.user
        user_contacts = UserContact.objects.filter(user=user).values_list(
            "contact_id", flat=True
        )
        contacts = Contact.objects.filter(id__in=user_contacts)

        return Response(ContactSerializer(contacts, many=True).data, status.HTTP_200_OK)
