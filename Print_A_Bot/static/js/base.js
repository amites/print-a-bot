var modal_id = '#ajax-modal';

function notify_data(data, width, delay) {
    if (data.msg.length > 0) {
        $.bootstrapGrowl(data.msg, {
            type: ((data.success) ? 'success' : 'error')
            ,align: 'center'
            ,width: typeof width !== 'undefined' ? width : 300
            ,delay: typeof delay !== 'undefined' ? delay : 8000
        });
    }
}

function load_ajax_modal(url, action, template_id, callback, title) {
    var modal_obj = $(modal_id);
    var content_obj = $(modal_id+' .modal-content');
    var loading_ids = {
        'bg_id': 'loading-modal',
        'bar_id': 'loading-bar'
    };

    var template = Handlebars.compile($('#template-loading-modal').html());
    $('body').append(template(loading_ids));

    $.get(url, function(data) {
        $('#' + loading_ids.bg_id).remove();
        $('#' + loading_ids.bar_id).remove();
        if (action === 'log') {
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
            ,msg: 'Failed to load page, please try again later.'
        });
        return false;
    });
}

function bind_modal(selector) {
    // {# Set a default selector string. #}
    selector = typeof selector !== 'undefined' ? selector : '[data-toggle="modal"][data-href]';

    var obj = $(this);
    var selector_obj = $(selector);

    selector_obj.on('click', function () {
        var url = $(this).attr('data-href');
        var action = $(this).attr('data-action') || false;
        load_ajax_modal(url, action, null, null, obj.text())

        var event = selector_obj.attr('data-event');
        // {# console.log('event: '+event); #}
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

// Handlebars helpers //

Handlebars.registerHelper('to_lower', function(str) {
    return str.toLowerCase();
});

Handlebars.registerHelper('to_upper', function(str) {
    return str.toUpperCase();
});

Handlebars.registerHelper('to_title', function(str) {
    return str.charAt(0).toUpperCase() + str.substring(1);
});

Handlebars.registerPartial('waiting', $('#template-waiting').html());

Handlebars.registerHelper('if_equals', function(v1, v2, options) {
  if(v1 === v2) {
    return options.fn(this);
  }
  return options.inverse(this);
});
