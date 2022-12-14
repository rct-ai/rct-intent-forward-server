var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function () {
    $messages.mCustomScrollbar();
    setTimeout(function () {
        fakeMessage("<div>请开始你的对话~</div>");
    }, 100);
});

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
        m = d.getMinutes();
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
}

function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
        return false;
    }
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();
    setTimeout(function () {
        jinaMessage(msg);
    }, 1000 + (Math.random() * 20) * 100);
}

$('.message-submit').click(function () {
    insertMessage();
});

$(window).on('keydown', function (e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    }
})


function fakeMessage(msg) {
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message loading new"><figure class="avatar"><img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function () {
        $('.message.loading').remove();
        $('<div class="message new"><figure class="avatar"><img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure>' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        updateScrollbar();
    }, 200);
}


function jinaMessage(question) {
    if ($('.message-input').val() != '') {
        return false;
    }

    $('<div class="message loading new"><figure class="avatar"><img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    $.ajax({
        type: "POST",
        url: $('#jina-server-addr').val() + "/api-v1/bot/get_response/",
        data: JSON.stringify({"text":question}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
    }).success(function (data, textStatus, jqXHR) {
        console.info(data)
	var lent=data["text"].length
	var choose_ans = Math.floor(Math.random() * lent)
        $('.message.loading').remove();
        $('<div class="message new">' +
            '<figure class="avatar">' +
            '<img src="https://api.jina.ai/logo/logo-product/jina-core/logo-only/colored/Product%20logo_Core_Colorful%402x.png" /></figure>' +
            '<div class="question">' + data["similar_question"][choose_ans] + '</div>' +
            data["text"][choose_ans] +
            '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        updateScrollbar();
    }).fail(function () {
        setTimeout(function () {
            fakeMessage("Connection failed, did you run <pre>jina hello chatbot</pre> on local? Is your address <pre>" + $('#jina-server-addr').val() + "</pre> ?");
        }, 100);
    });
}
