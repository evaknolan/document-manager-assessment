from django.shortcuts import render

from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from file_versions.models import FileVersion
from .serializers import FileVersionSerializer

class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = FileVersionSerializer
    queryset = FileVersion.objects.all()
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        fileversions = FileVersion.objects.all()
        serializer = FileVersionSerializer(fileversions, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        fileversion_serializer = FileVersionSerializer(data=request.data)
        if fileversion_serializer.is_valid():
            # check if another version of the file exisits 
            existing_files = FileVersion.objects.filter(file_path=request.data.get('file_path'))
            version = len(existing_files) + 1 if existing_files else 1
            fileversion_serializer.save(version_number=version)
            return Response(fileversion_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', fileversion_serializer.errors)
            return Response(fileversion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)