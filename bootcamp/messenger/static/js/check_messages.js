$(function () {
    function check_messages() {
        $.ajax({
            url: '/messages/check/',
            cache: false,
            success: function (data) {
                $("#unread-count").text(data);
            },
            complete: function () {
                window.setTimeout(check_messages, 60000);
            }
        });
    };
    check_messages();
});

// 60秒检查一次当前登陆用户是否有未读邮件
// 注意写法
// ajax完成的时候，设定一个定时器, 然后再递归调用