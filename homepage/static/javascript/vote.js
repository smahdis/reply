function vote() {
    post_pk = $(this).attr("pk");
    vote_type = $(this).attr("vote_type");
    vote_btn = $(this);
    id = $(this).id;
    this_parent = $(this).parent;

    $.ajax({
        url: '/ajax/vote/',
        data: {
            'pk': post_pk,
            'vote_type': vote_type
        },
        dataType: 'json',
        success: function (data) {
            if (data.self_voting) {
                vote_btn.popover({
                    content: 'نمیتوانید به پست خودتان رای دهید.',
                    toggle: 'popover',
                    trigger: 'manual focus',
                    container: 'body', // Popover scrolls with body
                    placement: 'auto right'
                }).popover("toggle");
                return;
            }
            $('button[pk = ' + post_pk + ']').siblings("div").html(data.number_of_votes);
            switch (data.vt) {
                case 0:
                    if (vote_type == -1) {
                        $('button[pk = ' + post_pk + ']').find('#upvote-img').attr('src', upvote);
                        $('button[pk = ' + post_pk + ']').find('#downvote-img').attr('src', downvote);
                    }
                    else {
                        $('button[pk = ' + post_pk + ']').find('#upvote-img').attr('src', upvote);
                        $('button[pk = ' + post_pk + ']').find('#downvote-img').attr('src', downvote);
                    }
                    break;
                case 1:
                    $('button[pk = ' + post_pk + ']').find('#upvote-img').attr('src', upvote_marked);
                    $('button[pk = ' + post_pk + ']').find('#downvote-img').attr('src', downvote);
                    break;
                case -1:
                    $('button[pk = ' + post_pk + ']').find('#upvote-img').attr('src', upvote);
                    $('button[pk = ' + post_pk + ']').find('#downvote-img').attr('src', downvote_marked);
                    break;
            }

        },
        error: function (data) {

        }
    });
}


$(document).ready(function() {
    $('.vote-c').click(vote);
});