/* Javascript for P3eXBlock. */
function P3eXBlock(runtime, element) {

    // Saving the URL of the handler
    var urlValid = runtime.handlerUrl(element, 'validate_studio');

    function validate_studio(eventObject) {
        $.ajax({
            type: "POST",
            url: urlValid,
            data: JSON.stringify(4),
            success: alert("ok")
        });
    }

    $(function ($) {
        /* Here's where you'd do things on page load. */
        $("#btn_valid_studio").click(validate_studio);
    });
}