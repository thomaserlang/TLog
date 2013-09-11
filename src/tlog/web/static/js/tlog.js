function kFormatter(num) {
    return num > 999 ? (num/1000).toFixed(1) + 'K' : num
}
function change_status(obj) {
    $.post('/log_group/change_status', $(obj).children('form').serialize(), function(data){
    });
    if ($(obj).hasClass('resolved') == true) {
        $(obj).removeClass('resolved').addClass('unresolved');
        $(obj).parents('.log_group').find('.message').removeClass('resolved_text');
    } else {
        $(obj).removeClass('unresolved').addClass('resolved');
        $(obj).parents('.log_group').find('.message').addClass('resolved_text');
    }
}

function update_time_ago() {
    $('time.timeago').timeago();
    setTimeout(
        function(){
            update_time_ago();
        },
        1000
    )
}