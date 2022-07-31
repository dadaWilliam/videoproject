from django.http import Http404
from video.models import Video
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

class BlockInvalidVideoMiddleware(MiddlewareMixin):
    def process_request(self, request):
        invalid_videos = Video.objects.filter(status=1).values('id')# status=1 未发布
        if invalid_videos:
            for invalid_video in invalid_videos:
                if request.path == '/video/detail/' + str(invalid_video['id']) +'/':
                    return render(request, 'editing.html', {'msg': "视频正在修改中..."})
                else:
                    pass
        pass



