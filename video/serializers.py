from rest_framework import serializers
from .models import Video, Classification
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    """用户的序列化器"""
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = '__all__'

class ClassificationSerializer(serializers.ModelSerializer):
    """分类的序列化器"""
    url = serializers.HyperlinkedIdentityField(view_name='classification-detail')

    class Meta:
        model = Classification
        fields = '__all__'

class VideoSerializer(serializers.HyperlinkedModelSerializer):
    """视频的序列化器"""
    # classification 的嵌套序列化字段
    classification = ClassificationSerializer(read_only=True)
    # classification 的 id 字段，用于创建/更新 category 外键
    classification_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)

    # category_id 字段的验证器
    def validate_classification_id(self, value):
        # 数据存在且传入值不等于None
        if not Classification.objects.filter(id=value).exists() and value != None:
            raise serializers.ValidationError("classification with id {} not exists.".format(value))
        return value

    class Meta:
        model = Video
        exclude = ['index_show',]
        #fields = '__all__'
