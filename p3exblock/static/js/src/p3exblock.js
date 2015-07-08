/* Javascript for P3eXBlock. */
function P3eXBlock(runtime, element) {

    // Saving the URL of the handler
    var urlValid1 = runtime.handlerUrl(element, 'validate_phase1');
    var urlValid2 = runtime.handlerUrl(element, 'validate_phase2');
    var urlValid3 = runtime.handlerUrl(element, 'validate_phase3');

    var currentPhase = 0;

    function init_phase() {
        currentPhase = $(".phase-container").attr("data-phaseNumber");

        // Smoothly move to the top
        $("html, body").animate({ scrollTop: 0 }, "slow");

        // Setting the right handler to call when #btn_valid id clicked
        if (currentPhase == 1) {
            $('#btn_valid', element).click(validate_phase1);
        } else if (currentPhase == 2) {
            $('#btn_valid', element).click(validate_phase2);
        } else if (currentPhase == 3) {
            $('#btn_valid', element).click(validate_phase3);
        }

        // Updating the counter of points the user can distribute during this phase
        $(".counter_input").change(function () {
            var total_points_to_use = 10;
            if (currentPhase==3)
                total_points_to_use = 30;

            var sum_points_given = 0;
            $(".counter_input").each(function () {
                sum_points_given += parseInt($(this).val());
            })

            var remaining_points = total_points_to_use - sum_points_given;
            $("#counter_value").text(remaining_points);

            if (remaining_points==0) {
                $("#btn_valid").prop( "disabled", false );
                $("#btn_valid").prop( "title", "");
            } else{
                $("#btn_valid").prop( "disabled", true );
                $("#btn_valid").prop( "title", "Please distribute all points before validating.");
            };
        });
        // Prevent entering letters, negative or decimal numbers
        $(".counter_input").keypress(function () {
            return false;
        });

        //Enable a textarea to submit a better solution
        $(".wrong-solution").click(function () {
            $(this).parent().siblings(".new-solution").slideToggle("slow");
        });

        // About scrolling of reverse_counter
        // $(window).on("scroll", function() {
        //     var w = $(window);
        //     var counter = $("#reverse_counter");
        //     var distanceFromTop = counter.offset().top - w.scrollTop();
        //     console.log("distanceFromTop = counter.offset().top - w.scrollTop() : ", distanceFromTop, " = ", counter.offset().top, " - ", w.scrollTop());
            
        //     if (distanceFromTop < 100) {
        //         counter.addClass("reverse_counter-fixed");
        //     } else {
        //         counter.removeClass("reverse_counter-fixed");
        //     }
        // });
    }

    function validate_phase1(eventObject) {
        $.ajax({
            type: "POST",
            url: urlValid1,
            data: JSON.stringify([
                // Sending to server a list of JSON object, each contening the answer 
                // gave by the student and grade related to a question
                {'answer': $('#r1').html(), 'question_grade': $('#note_saver1').val()},
                {'answer': $('#r2').html(), 'question_grade': $('#note_saver2').val()},
                {'answer': $('#r3').html(), 'question_grade': $('#note_saver3').val()}
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
        var answer_grades = [];
        var clue_grades = [];
        var new_solutions = [];

        $(".question_block").each(function () {
            answer_grades.push( $(this).find(".answer_grade").val() );
            clue_grades.push( $(this).find(".clue_grade").val() );
            new_solutions.push( $(this).find(".new-solution").val() );
        });

        $.ajax({
            type: "POST",
            url: urlValid3,
            data: JSON.stringify({answer_grades, clue_grades, new_solutions}),
            success: change_phase
        });
    }

    function change_phase(html_content) {
        // Replacing the html content by the html of the new phase
        $(".p3exblock_block").replaceWith(html_content);
        init_phase();
    }


    $(function ($) {
        /* Here's where you'd do things on page load. */
        init_phase();
    });
}