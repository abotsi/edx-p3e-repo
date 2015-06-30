/* Javascript for P3eXBlock. */
function P3eXBlock(runtime, element) {

    // Saving the URL of the handler
    var urlValid1 = runtime.handlerUrl(element, 'validate_phase1');
    var urlValid2 = runtime.handlerUrl(element, 'validate_phase2');
    var urlValid3 = runtime.handlerUrl(element, 'validate_phase3');

    function change_phase(html_content) {
        // Replacing the html content by the html of the new phase
        $(".p3exblock_block").replaceWith(html_content);
        $("html, body").animate({ scrollTop: 0 }, "slow");
        bind_btn_to_handler()
    }

    function bind_btn_to_handler() {
        // Setting the handler to call on #btn_valid click
        if ($("#phase1").length) {
            $('#btn_valid', element).click(validate_phase1);
        } else if ($("#phase2").length) {
            $('#btn_valid', element).click(validate_phase2);
        } else if ($("#phase3").length) {
            $('#btn_valid', element).click(validate_phase3);
        }
    }

    function validate_phase1(eventObject) {
        $.ajax({
            type: "POST",
            url: urlValid1,
            data: JSON.stringify([
                // Sending to server a list of JSON object, each contening the answer 
                // gave by the student and grade related to a question
                {'answer': $('#r1').val(), 'question_grade': $('#note_saver1').val()},
                {'answer': $('#r2').val(), 'question_grade': $('#note_saver2').val()},
                {'answer': $('#r3').val(), 'question_grade': $('#note_saver3').val()}
            ]),
            success: change_phase
        });
    }

    function validate_phase2(eventObject) {
        $.ajax({
            type: "POST",
            url: urlValid2,
            data: JSON.stringify({
                "question": $('#q').val(), 
                "answer": $('#r').val()
            }),
            success: change_phase
        });
    }

    function validate_phase3(eventObject) {
        lst_of_grade = []
        $(".note_saver").each(function () {
            lst_of_grade += $(this).val();
        })

        $.ajax({
            type: "POST",
            url: urlValid3,
            data: JSON.stringify(lst_of_grade),
            success: change_phase
        });
    }


    $(function ($) {
        /* Here's where you'd do things on page load. */
        bind_btn_to_handler();

        // Updating the counter of points the user can distribute during this phase
        $(".counter_input").change(function () {
            var current_phase = $(".phase-container").attr("data-phaseNumber");
            var total_point_to_use = 10*current_phase;
            var sum_points_given = 0;

            $(".counter_input").each(function () {
                sum_points_given += parseInt($(this).val());
            })

            var remaining_points = total_point_to_use - sum_points_given;
            $("#counter_value").text(remaining_points);

            if (remaining_points==0) {
                $("#btn_valid").prop( "disabled", false );
                $("#btn_valid").prop( "title", "Please distribute all points before validating.");
            } else{
                $("#btn_valid").prop( "disabled", true );
                $("#btn_valid").prop( "title", "");
            };
        });

        $(".counter_input").keypress(function () {
            return false;
        });
    });
}
