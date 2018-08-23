$(function () {
    $("#send").submit(function () {
        $.ajax({
            url: '/messages/send/',
            data: $("#send").serialize(),
            cache: false,
            type: 'post',
            success: function (data) {
                $(".send-message").before(data);
                $("input[name='message']").val('');
                $("input[name='message']").focus();
            }
        });
        return false;
    });
});

// #send是inbox的form
// form.serialize(): 把form数据序列化
// ajax提交，返回数据插入到send-message元素之前, 然后设置输入消息的input值为空