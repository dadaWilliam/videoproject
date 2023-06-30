from notifications.models import Notification
from rest_framework import serializers
from .models import Video, Classification
from users.models import User
from history.models import History


class UserSerializer(serializers.ModelSerializer):
    """用户的序列化器"""
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        exclude = ['password', ]
        # new !!!
        # fields = '__all__'


class ClassificationSerializer(serializers.HyperlinkedModelSerializer):
    """分类的序列化器"""
    url = serializers.HyperlinkedIdentityField(
        view_name='classification-detail')
    # classification 的嵌套序列化字段

    # videos = serializers.SerializerMethodField()
    #
    # def get_videos(self, obj):
    #     videos = Video.objects.filter(classification_id=obj.id, status=0)
    #     if videos is not None and len(videos) > 0:
    #         return VideoInfoSerializer(videos, many=True).data
    #     else:
    #         return ""

    class Meta:
        model = Classification
        exclude = ['vip', 'status']
        # fields = '__all__'


# class ClassificationLessSerializer(serializers.ModelSerializer):
#     """分类的序列化器"""
#     url = serializers.HyperlinkedIdentityField(
#         view_name='classification-detail')

#     class Meta:
#         model = Classification
#         exclude = ['vip', ]
#         # fields = '__all__'

# class VideoInfoSerializer(serializers.HyperlinkedModelSerializer):
#     """于分类列表中引用的嵌套序列化器"""
#     # classification = ClassificationLessSerializer(read_only=True)
#     # # # classification 的 id 字段，用于创建/更新 category 外键
#     # classification_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)
#     class Meta:
#         model = Video
#         fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    # """分类的序列化器"""
    #url = serializers.HyperlinkedIdentityField(view_name='history-detail')
    video = serializers.SerializerMethodField()

    def get_video(self, obj,):
        # print(obj.user.vip)
        if obj.user.vip:
            video = Video.objects.filter(
                id=obj.object_id, status=0)
        else:
            video = Video.objects.filter(
                id=obj.object_id, status=0, vip=obj.user.vip)
        if video is not None and len(video) > 0:
            return VideoSerializer(video, many=True, context=self.context).data
        else:
            return ""

    class Meta:
        model = History
        #exclude = ['content_object',]
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    # """分类的序列化器"""
    #url = serializers.HyperlinkedIdentityField(view_name='history-detail')
    video = serializers.SerializerMethodField()

    def get_video(self, obj, ):
        vip = obj.recipient.vip
        # print(obj.recipient.vip)
        if vip:
            video = Video.objects.filter(id=obj.target_object_id, status=0)
        else:
            video = Video.objects.filter(
                id=obj.target_object_id, status=0, vip=vip)
        if video is not None and len(video) > 0:

            return VideoSerializer(video, many=True, context=self.context).data
        else:
            return ""

    class Meta:
        model = Notification
        fields = '__all__'


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    """视频的序列化器"""
    # classification 的嵌套序列化字段
    classification = ClassificationSerializer(read_only=True)
    # # classification 的 id 字段，用于创建/更新 category 外键
    classification_id = serializers.IntegerField(
        write_only=True, allow_null=True, required=False)
    #create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    # category_id 字段的验证器
    def validate_classification_id(self, value):
        # 数据存在且传入值不等于None
        if not Classification.objects.filter(id=value).exists() and value != None:
            raise serializers.ValidationError(
                "classification with id {} not exists.".format(value))
        return value

    class Meta:
        model = Video
        exclude = ['index_show', 'vip', 'status']
        #fields = '__all__'
