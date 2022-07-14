from django.http import Http404
from video.models import Video
from django.utils.deprecation import MiddlewareMixin

class BlockInvalidVideoMiddleware(MiddlewareMixin):
    def process_request(self, request):
        invalid_videos = Video.objects.filter(status=1).values('id')# status=1 未发布
        if invalid_videos:
            for invalid_video in invalid_videos:
                if request.path == '/video/detail/' + str(invalid_video['id']) +'/':
                    raise Http404()
                else:
                    pass
        pass



