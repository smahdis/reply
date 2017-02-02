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
                // $('.vote-c').parent().not(vote_btn).popover('hide').next('.popover').remove('.popover');
                // vote_btn.parent().attr({
                //     'data-placement': 'auto right',
                //     // 'data-toggle': 'popover',
                //     'data-trigger': 'manual focus',
                //     'data-original-title':"Salam khoobi khoobam?",
                //     'data-content': 'نمیتوانید به پست خودتان رای دهید.',
                //     'container':'body'
                // });
                // vote_btn.parent().popover("toggle");
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
var lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer pharetra tellus sit amet massa efficitur placerat. Cras mollis enim neque, luctus porttitor neque suscipit eu. Aliquam rhoncus nisi sit amet dui porttitor tincidunt in at diam. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Quisque elementum dui eget odio ultricies eleifend at sit amet arcu.";

$(document).ready(function() {
    $('.vote-c').click(vote);

    $("#example-body").popover({
        content: lorem,
        container: 'body' // Popover scrolls with body
    });

});