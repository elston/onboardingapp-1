function highlight_box2(checked, id_checked, services){
    var it;
    for (k in services) {
        it = services[k].toLowerCase() + 'Box';
        document.getElementById(it).style.border = "2px solid #2a8fbb";
    }

    document.getElementById(checked).style.border = "4px solid #2a8fbb";
    document.getElementById(id_checked).checked = true;

    //
    service = document.getElementById(id_checked);
    get_form(service.value);
}

$(':radio[name=s_name]').on('change', function(){
    if (this.checked) {
        get_form(this.value);
    }
});

function get_form(name) {
    $("#add-service-form").find('.error').remove();

    $.ajax({
        type: 'post',
        url: '/service/get-form/',
        data: {'s_name': name},
        success: function(result) {
            var form = result.form;
            var html = '';

            for (var k in form) {
                html += '<div class="form-group">' + form[k] + '</div>';
            }
            $("#service-form").html(html);
        },
        error: function(data, status) {
            console.log(status);
        },

    });
}

$("#add-service-form").on("submit", function(e) {
    if (e.target.name.value != undefined) {

        var frm = $("#add-service-form");
        $("#add-service-form").find('.error').remove();

        $.ajax({
            type: "post",
            url: "/team/" + e.target.team.value + "/service/" + e.target.name.value + "/add",
            data: frm.serialize(),
            beforeSend: function(){
                $('#loading-data').modal();
            },
            success: function(result) {
                $('#loading-data').modal("hide");

                if (result.redirect) {
                    location.href = result.url;
                } else {
                    location.reload();
                }
            },
            error: function(data, status) {
                $('#loading-data').modal("hide");

                var errors = JSON.parse(data.responseText);

                if (errors['err']) {
                    $("#service-form").before('<div class="error" style="color: red;">' + errors['err'] + '</div>')
                } else {
                    for (var k in errors) {
                        $("#add-service-form").find('input[name=' + k + ']').before('<div class="error" style="color: red;">' + errors[k] + '</div>');
                    }
                }

            },
        });

    }
    return false;
});

function key_input() {
    link_val = "https://trello.com/1/authorize?key=" + $('#id_key').val() + "&name=MVPproject&expiration=never&response_type=token&scope=read,write";
    $("#a_token_link").attr("href", link_val);
    //$('#token_placeholder').text($('#id_key').val());
}

$('#search-field').on('input', function(e) {

    $.ajax({
        type: "post",
        url: "/service/search",
        data: {'search': e.target.value},
        success: function (result) {

            var services = result.services;
            var html = '';
            var htmlxs = '';

            for (k in services) {
                htmlxs += '<div class="col-lg-4 col-md-4 col-sm-4 col-xs-6"><div class="text-center"><label>' + services[k] + '</label></div><div class="radio radio-primary text-center"><input onclick="radio_click(this)" type="radio" id="id_' + services[k] + '" value="' + services[k] + '" name="s_name" aria-label="Single radio One"><label></label></div></div>';

                html += '<div class="col-lg-4 col-md-4 col-sm-4 col-xs-4"><div id="' + services[k].toLowerCase() + 'Box" class="tools-border" onclick="highlight_box2(' + "'" + services[k].toLowerCase() + 'Box' + "'" + ', ' + "'" + 'id_' + services[k] + "'" + ',' + Array[services] + ')"><img src="/static/new/img/team/' + services[k].toLowerCase() + '-sm.png" class="img-responsive"></div><div class="radio radio-primary text-center"><input type="radio" id="id_' + services[k] + '" value="' + services[k] + '" name="s_name" aria-label="Single radio One"><label></label></div></div>';

            }

            $("#services").html(html);
            $("#services-xs").html(htmlxs);

        },
    });

});

function radio_click(e){
    if (e.checked) {
        get_form(e.value);
    }
}

function remove_service(s_id, t_id)
{
    var r = confirm("Are you sure to remove this service?");
    if (r == true) {
        $.ajax({
            type: "post",
            url: "/service/remove",
            data: {'s_id': s_id, 't_id': t_id},
            beforeSend: function(){
                $('#loading-data').modal();
            },
            success: function (data) {
                $('#loading-data').modal("hide");
                location.reload();
            },
            error: function(data, status) {
                $('#loading-data').modal("hide");
                location.reload();
            }
        });
    } else {
        return false;
    }
}
