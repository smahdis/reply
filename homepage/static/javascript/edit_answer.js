function vote() {
    $.ajax({
        url: '/ajax/edit_answer/',
        data: {
            'pk': post_pk,
            'vote_type': vote_type
        },
        dataType: 'json',
        success: function (data) {

        },
        error: function (data) {

        }
    });
}