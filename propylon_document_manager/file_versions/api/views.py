from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from file_versions.models import FileVersion
from .serializers import FileVersionSerializer
from ..permissions import FilePermissions

class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, FilePermissions]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        fileversions = FileVersion.objects.filter(user=request.user)
        serializer = self.serializer_class(fileversions, many=True)
        return Response(serializer.data)

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
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated, FilePermissions]
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        path = kwargs.get('path')
        version = request.GET.get('version') if request.GET.get('version') else 1 #TODO else get latest?
        file = FileVersion.objects.get(file_path=path, version_number=version, user=request.user)
        if file:
            file_location = file.file.path
            try:    
                with open(file_location, 'r') as f:
                    file_data = f.read()
                return Response(file_data, status=status.HTTP_200_OK)
            except IOError:
                return Response('file not found', status=status.HTTP_404_NOT_FOUND)
        else:
            return Response('file not found', status=status.HTTP_404_NOT_FOUND)
        