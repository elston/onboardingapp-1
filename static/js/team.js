$( "#create-team-form" ).on('submit', function() {
    var frm = $("#create-team-form");
    $("#create-team-form").find('.error').remove();

    $.ajax({
        type: frm.attr('method'),
        url: frm.attr('action'),
        data: frm.serialize(),
        success: function (result) {
            location.href = result.href;
        },
        error: function (data, status) {
            var json = JSON.parse(data.responseText);
            var errors = json['response'];

            if (data.status == 400) {
                for (var k in errors) {
                    $("#create-team-form").find('input[name=' + k + ']').before('<div class="error" style="color: red;">' + errors[k] + '</div>');
                }
            } else {
                location.reload();
            }
        },
    });
    return false;
});

function check(){
    $.ajax({
        type: 'post',
        url: '/team/limit/check',
        data: {},
        success: function (result) {
            openbox('', 0);
        },
        error: function (data, status) {
            var json = JSON.parse(data.responseText);
            var error = json['response'];
            $("#messages-wrapper").append('<div class="alert alert-danger alert-message" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + error + '</div>');
        },
    });
}

function invite_team_member(email, team_id)
{

    var data = '';
    if (email) {
        data = {'user_email': email, 'team': team_id};
    } else {
        var frm = $("#user-invite-form");
        $("#user-invite-form").find('.error').remove();
        data = frm.serialize();
    }

    $.ajax({
        type: "post",
        url: "/user/invite",
        data: data,
        success: function (result) {
            location.reload();
        },
        error: function (data, status) {
            if (data.status == 400) {
                var json = JSON.parse(data.responseText);
                var errors = json['response'];

                for (var k in errors) {
                    $("#user-invite-form").find('input[name=' + k + ']').before('<div class="error" style="color: red;">' + errors[k] + '</div>');
                }
            } else {
                location.reload();
            }
        },
    });
    return false;
}

function remove_member(m_id, t_id)
{
    var r = confirm("Are you sure to remove this member?");
    if (r == true) {
        $.post('/team/member/remove', {'m_id': m_id, 't_id': t_id})
            .success(function(result){
                location.reload();
            })
            .error(function(data, status){
                location.reload();
            });
    } else {
        return false;
    }
}
