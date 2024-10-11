$(document).ready(function() {
    $("#send-button").click(function() {
        var message = $("#message-input").val();


        $("#chat-container").append("<p class='user'><strong>You:<br></strong> " + message + "</p>");

        // Add typing indicator
        var typingIndicator = $("<p class='bot typing'><strong>Bot:<br></strong> <span class='typing-dots'>...</span></p>");
        $("#chat-container").append(typingIndicator);

        $.ajax({
            url: "/chat",
            type: "POST",
            dataType: "json",
            data: { message: message },
            success: function(response) {
                typingIndicator.remove();
                $("#chat-container").append("<p class='bot'><strong>Bot:<br></strong> <span class='typing'>" + response.message + "</span></p>");
                $("#message-input").val("");
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});
