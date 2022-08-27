from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from users.models import User
from video.models import Video, Classification


def avatar_file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('头像文件太大了，请限制在2M之内')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(min_length=2,max_length=30,
                               error_messages={
                                   'min_length': '用户名不少于2个字符',
                                   'max_length': '用户名不能多于30个字符',
                                   'required': '用户名不能为空',
                               },
                               widget=forms.TextInput(attrs={'placeholder': '请输入用户名'}))
    password = forms.CharField(min_length=8,max_length=30,
                               error_messages={
                                   'min_length': '密码不少于8个字符',
                                   'max_length': '密码不能多于30个字符',
                                   'required': '密码不能为空',
                               },
                               widget=forms.PasswordInput(attrs={'placeholder': '请输入密码'}))

    class Meta:
        model = User
        fields = ['username', 'password', ]

    error_messages = {'invalid_login': '用户名或密码错误', }


class VideoPublishForm(forms.ModelForm):
    title = forms.CharField(min_length=4, max_length=200, required=True,
                              error_messages={
                                  'min_length': '至少4个字符',
                                  'max_length': '不能多于200个字符',
                                  'required': '标题不能为空'
                              },
                              widget=forms.TextInput(attrs={'placeholder': '请输入内容'}))
    desc = forms.CharField(min_length=4, max_length=200, required=True,
                              error_messages={
                                  'min_length': '至少4个字符',
                                  'max_length': '不能多于200个字符',
                                  'required': '描述不能为空'
                              },
                              widget=forms.Textarea(attrs={'placeholder': '请输入内容'}))
    cover = forms.ImageField(required=True,
                             error_messages={
                                 'required': '封面不能为空'
                             },
                             widget=forms.FileInput(attrs={'class' : 'n'}))
    status = forms.CharField(min_length=1, max_length=1, required=False,
                             widget=forms.HiddenInput(attrs={'value':'0'}))
    class Meta:
        model = Video
        fields = ['title', 'desc','status', 'cover', 'classification']


class VideoEditForm(forms.ModelForm):
    title = forms.CharField(min_length=4, max_length=200, required=True,
                              error_messages={
                                  'min_length': '至少4个字符',
                                  'max_length': '不能多于200个字符',
                                  'required': '标题不能为空'
                              },
                              widget=forms.TextInput(attrs={'placeholder': '请输入内容'}))
    desc = forms.CharField(min_length=4, max_length=200, required=True,
                              error_messages={
                                  'min_length': '至少4个字符',
                                  'max_length': '不能多于200个字符',
                                  'required': '描述不能为空'
                              },
                              widget=forms.Textarea(attrs={'placeholder': '请输入内容'}))
    cover = forms.ImageField(required=True,
                             error_messages={
                                 'required': '封面不能为空'
                             },
                             widget=forms.FileInput(attrs={'class' : 'n'}))

    status = forms.CharField(min_length=1,max_length=1,required=False,
                             widget=forms.HiddenInput())
    view_count = forms.IntegerField(required=True, error_messages={
                                 'required': '观看次数不能为空'
                             },)
    index_show = forms.IntegerField(required=True, error_messages={
        'required': '首页显示不能为空'
    }, )
    # classification = forms.ModelChoiceField(queryset=Classification.objects.all())
    # classification = forms.CharField(min_length=1,max_length=1,required=False,
    #                          widget=forms.HiddenInput())

    class Meta:
        model = Video
        fields = ['title', 'desc', 'status', 'cover','classification','view_count','index_show',]



class UserAddForm(forms.ModelForm):
    username = forms.CharField(min_length=2,max_length=30,
                               error_messages={
                                   'min_length': '用户名不少于2个字符',
                                   'max_length': '用户名不能多于30个字符',
                                   'required': '用户名不能为空',
                               },
                               widget=forms.TextInput(attrs={'placeholder': '请输入用户名'}))
    password = forms.CharField(min_length=8,max_length=30,
                               error_messages={
                                   'min_length': '密码不少于8个字符',
                                   'max_length': '密码不能多于30个字符',
                                   'required': '密码不能为空',
                               },
                               widget=forms.PasswordInput(attrs={'placeholder': '请输入密码'}))
    expire = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    class Meta:
        model = User
        fields = ['username', 'password', 'is_staff', 'expire']


def username_validate(value):
    if value == "admin":
        raise ValidationError('不能编辑超级管理员')


class UserEditForm(forms.ModelForm):
    username = forms.CharField(min_length=2, max_length=30, required=True,
                               validators=[username_validate],
                              error_messages={
                                  'min_length': '至少2个字符',
                                  'max_length': '不能多于30个字符',
                                  'required': '用户名不能为空'
                              },
                              widget=forms.TextInput(attrs={'placeholder': '请输入用户名'}))
    expire = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    
    nickname = forms.CharField(min_length=1,max_length=20,required=False,
                               error_messages={
                                   'min_length': '昵称至少1个字符',
                                   'min_length': '昵称不能多于20个字符',
                               },
                               widget=forms.TextInput())
    avatar = forms.ImageField(required=False, validators=[avatar_file_size],
                              widget=forms.FileInput(attrs={'class' : 'n'}))
    email = forms.EmailField(required=False,
                             error_messages={
                                 'invalid': '请输入有效的Email地址',
                             },
                             widget=forms.EmailInput())
    # gender = forms.CharField(min_length=1,max_length=1,required=False,
    #                          widget=forms.HiddenInput())

    mobile = forms.CharField(min_length=11,max_length=11,required=False,
                             error_messages={
                                 'min_length': '请输入11位手机号',
                                 'max_length': '请输入11位手机号',
                             },
                             widget=forms.NumberInput())
    class Meta:
        model = User
        fields = ['username', 'is_staff', 'expire', 'avatar', 'nickname', 'email', 'mobile', 'gender', 'subscribe']


class ClassificationAddForm(forms.ModelForm):
    title = forms.CharField(min_length=2, max_length=30, required=True,
                            error_messages={
                                'min_length': '至少2个字符',
                                'max_length': '不能多于30个字符',
                                'required': '不能为空'
                            },
                            widget=forms.TextInput(attrs={'placeholder': '请输入分类名称'}))
    class Meta:
        model = Classification
        fields = ['title', 'status' ]

class ClassificationEditForm(forms.ModelForm):
    title = forms.CharField(min_length=2, max_length=30, required=True,
                              error_messages={
                                  'min_length': '至少2个字符',
                                  'max_length': '不能多于30个字符',
                                  'required': '不能为空'
                              },
                              widget=forms.TextInput(attrs={'placeholder': '请输入分类名称'}))

    class Meta:
        model = Classification
        fields = ['title','status']