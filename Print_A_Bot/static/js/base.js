var modal_id = '#ajax-modal';

function load_ajax_modal(url, action, template_id, callback, title) {
    var modal_obj = $(modal_id);
    var content_obj = $(modal_id+' .modal-content');
    var loading_ids = {
        'bg_id': 'loading-modal',
        'bar_id': 'loading-bar'
    }

    var template = Handlebars.compile($('#template-loading-modal').html());
    $('body').append(template(loading_ids));

    $.get(url, function(data) {
        $('#' + loading_ids.bg_id).remove();
        $('#' + loading_ids.bar_id).remove();
        if (action == 'log') {
            var file_template = Handlebars.compile($('#template-log-display').html());
            var file_data = {
                title: typeof title !== 'undefined' ? title : ''
                ,data: data
                ,url: url
            };
            content_obj.html(file_template(file_data));
            modal_obj.css('max-height', '90%').css('overflow', 'scroll');
        } else if (template_id) {
            var template = Handlebars.compile($(template_id).html());
            content_obj.html(template(data));
        } else {
            content_obj.html(data);
        }

        modal_obj.modal('show');
        if (callback) {
            callback();
        }


        return true;
    }).fail(function() {
        $('#'+loading_ids['bg_id']).remove();
        $('#'+loading_ids['bar_id']).remove();
        notify_data({
            success: false
            ,msg: '{%trans 'Failed to load page, please try again later.' %}'
        })
        return false;
    });
}

function bind_modal(selector) {
    selector = typeof selector !== 'undefined' ? selector : '[data-toggle="modal"][data-href]';

    var obj = $(this);
    var selector_obj = $(selector);

    selector_obj.on('click', function () {
        var url = $(this).attr('data-href');
        var action = $(this).attr('data-action') || false;
        load_ajax_modal(url, action, null, null, obj.text())

        var event = selector_obj.attr('data-event');
        if (event) {
            $(document).trigger(event);
        }

    });
}


function show_modal_content(content, title, footer) {
    var modal_obj = $(modal_id);
    var content_obj = $(modal_id+' .modal-content');

    var template = Handlebars.compile($('#template-modal-content').html());
    var data = {
        title: title
        ,content: content
        ,footer: footer
    };

    content_obj.html(template(data));

    modal_obj.modal('show');
}
