$(document).ready(function() {

    $('.toolbar a').click(function (e) {
        var command = $(this).data('command');
        if (command == 'h1' || command == 'h2' || command == 'p' || command == 'blockquote' || command == 'code') {
            document.execCommand('formatBlock', false, command);
        }

        if (command == 'createlink' || command == 'insertimage') {
            url = prompt('Enter the link here: ', 'http:\/\/');
            document.execCommand($(this).data('command'), false, url);
        }
        else
            document.execCommand($(this).data('command'), false, null);
    });
});