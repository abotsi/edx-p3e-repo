/* Javascript for P3eXBlock. */
function P3eXBlock(runtime, element) {

    // Saving the URL of the handler
    var urlValid = runtime.handlerUrl(element, 'validate_studio');

    // Saving a virgin new question block 
    var new_block_html = $("#new_qb").clone().removeAttr("id");

    function send_new_question() {
        $.ajax({
            type: "POST",
            url: urlValid,
            data: JSON.stringify({
                "q": $(this).siblings('.question').text(), 
                "r": $(this).siblings('.answer').text()
            }),
            success: append_new_question_block
        });
    }

    function append_new_question_block(next_id) {
        var sent_block = $("#new_qb").removeAttr("id");
        sent_block.children(".textarea").attr("contentEditable", false);
        sent_block.children(".btn_submit_question").remove();
        sent_block.children(".num").text("#" + next_id + " :"); 

        $(".phase-container").append( new_block_html.clone().attr("id", "new_qb")[0].outerHTML );
        $("#new_qb div.question").focus();
        $(".btn_submit_question").click(send_new_question);
    }

    $(function ($) {
        /* Here's where you'd do things on page load. */
        $(".btn_submit_question").click(send_new_question);

    });
}