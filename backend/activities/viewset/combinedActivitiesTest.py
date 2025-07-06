from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response

from activities.modules.combined_activities import get_combined_activities
from activities.serializer import ActivitySerializer

class CombinedActivitiesTestView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    format_str = "%Y-%m-%d %H:%M:%S.%f%z"

    def list(self, request, *args, **kwargs):
        st_str = self.request.query_params.get("start")
        end_str = self.request.query_params.get("end")
        audio_policy = 0
        if 'audio_policy' in self.request.query_params:
            audio_policy = int(self.request.query_params.get("audio_policy"))
        print(f"audio_policy :{audio_policy}")
        alist = get_combined_activities(datetime.strptime(st_str+"+09:00", self.format_str),
                                       datetime.strptime(end_str+"+09:00", self.format_str), audio_policy)
        serializer = self.get_serializer(alist, many=True)
        return Response(serializer.data)    
