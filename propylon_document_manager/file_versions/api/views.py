from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, extend_schema

from file_versions.models import FileVersion
from .serializers import FileVersionSerializer
from ..permissions import FilePermissions

class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    get:
    Return list of all FileVersion objects requesting user has access to
    Token authentication header required

    post:
    Create a new FileVersion object
    If file_name and file_path already exist version number will be incremented
    Token authentication header required
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, FilePermissions]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    @extend_schema(
        description='Get list of all FileVersion objects requesting user has access to',
        responses={
            200:serializer_class(many=True),
            401: OpenApiResponse(description='Authentication credentials were not provided')
        }
    )
    def list(self, request, *args, **kwargs):
        fileversions = FileVersion.objects.filter(user=request.user)
        serializer = self.serializer_class(fileversions, many=True)
        return Response(serializer.data)

    @extend_schema(
        description='Create a new FileVersion object.If file_name and file_path already exist version number will be incremented',
        responses={
            201:serializer_class(),
            400: OpenApiResponse(description='The submitted data was not a file. Check the encoding type on the form.'),
            401: OpenApiResponse(description='Authentication credentials were not provided')
        }
    )
    def post(self, request, *args, **kwargs):
        fileversion_serializer = self.serializer_class(data=request.data)
        if fileversion_serializer.is_valid():
            # check if another version of the file exisits
            existing_files = FileVersion.objects.filter(file_path=request.data.get('file_path'), user=request.user)
            version = len(existing_files) + 1 if existing_files else 1
            fileversion_serializer.save(version_number=version)
            return Response(fileversion_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', fileversion_serializer.errors)
            return Response(fileversion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    get:
    Return FileVersion object with file_path matching request path
    If version query param is present on request corresponsing version is returned otherwise latest version is returned
    Token authentication header required
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, FilePermissions]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    @extend_schema(
        description='Get FileVersion object with file_path matching request path',
        parameters=[
            OpenApiParameter(name='version',location=OpenApiParameter.QUERY, description='Version Id', required=False, type=int)
        ],
        responses={
            200:serializer_class(),
            404: OpenApiResponse(description='File not found'),
            401: OpenApiResponse(description='Authentication credentials were not provided')
        }
    )
    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        try:
            if request.GET.get('version'):
                file = FileVersion.objects.get(file_path=path, version_number=request.GET.get('version'), user=request.user)
            else:
                file = FileVersion.objects.filter(file_path=path, user=request.user).order_by('-version_number').first()
            if not file:
                raise FileVersion.DoesNotExist
            file_location = file.file.path
            with open(file_location, 'r') as f:
                file_data = f.read()
            return Response(file_data, status=status.HTTP_200_OK)
        except (IOError, FileVersion.DoesNotExist):
            return Response('File not found', status=status.HTTP_404_NOT_FOUND)
