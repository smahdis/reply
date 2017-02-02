$(document).ready(function() {
    $('.profile-pic').initial({
        height: 24,
        width: 24,
        fontSize: 14,
        fontFamily: 'Tahoma, sans-serif',
    });

    String.prototype.toIndiaDigits = function () {
        var id = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
        return this.replace(/[0-9]/g, function (w) {
            return id[+w]
        });
    }
    elements = document.getElementsByClassName("days_ago");
    for (var i = 0; i < elements.length; i++) {
        value = elements[i].innerHTML;
        elements[i].innerHTML = value.toIndiaDigits();
    }


    $('[data-toggle="tooltip"]').tooltip();

    $("#submit_answer").click(function(event) {
        var details= document.getElementById("editor").innerHTML;
        // post_pk = post_pk;
        $.ajax({
            url: '/ajax/answer_question/',
            data: {
                'pk': post_pk,
                'content': $('#editor').html(),
            },
            dataType: 'json',
            success: function (data) {
                if(data.success)
                {
                    // window.location.href = data.redirect + data.pk;
                    add_answer(details, data.pk, data.color);
                }
            },
            error: function (data) {
            }
        });
        return true;
    });

});
