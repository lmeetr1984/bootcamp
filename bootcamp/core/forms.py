# coding:utf-8
from django import forms
from django.contrib.auth.models import User

# 注意，这里是modelform，
# 要求继承类必须定义一个meta类
class ProfileForm(forms.ModelForm):
    # 定义了一个字段，注意字段名和要传进来的字段要一致
    # required ： 表示 默认情况下，每个字段 类都假设必需有值，
    # 所以如果你传递一个空的值 , 不管是None 还是空字符串("") 
    #  clean() 将引发一个ValidationError 异常
    first_name = forms.CharField(

        # widget 最终会被翻译成一个html 表单元素
        # TextInput => <input type="text" ...>
        # attrs : 提供了input元素的一些属性，比如下面的代码增加class信息
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=False)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=False)
    job_title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False)
    email = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=75,
        required=False)
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False)
    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False)

    #  从模型中生成剩下的字段，因为模型自带，所以根本没有必要再次定义
    # 顺序是和fields 定义的顺序一致
    class Meta:
        model = User
        # 因为job_title， email， url 是profile的字段
        # 所以必须要求上面的字段定义
        fields = ['first_name', 'last_name', 'job_title',
                  'email', 'url', 'location', ]

# 修改密码的form
class ChangePasswordForm(forms.ModelForm):
    # 还定义了一个隐藏字段
    id = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Old password",
        required=True)

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New password",
        required=True)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm new password",
        required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    # 可以重写模型表单的clean() 来提供额外的验证，方法和普通的表单一样。
    def clean(self):
        # 首先调用基类的方法
        super(ChangePasswordForm, self).clean()

        # 验证新旧密码
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')

        # id用来获取user
        user = User.objects.get(pk=id)
        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class(['Old password don\'t match'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class(['Passwords don\'t match'])

        # 注意返回数据
        return self.cleaned_data
