from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import IOU
from .serializers import IOUSerializer

class IOUListCreateView(generics.ListCreateAPIView):
    queryset = IOU.objects.all()
    serializer_class = IOUSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(lender=self.request.user)

class IOUDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = IOU.objects.all()
    serializer_class = IOUSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
