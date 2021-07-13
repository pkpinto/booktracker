$(document).ready(function() {

    $(function() {
        $(".request-delete").click(function() {
            $.ajax({
                url: $(this).attr("href"),
                method: "delete",
                success: function(response) {
                    alert(JSON.stringify(response));
                    location.reload();
                }
            });
        });
    });

    $(function() {
        $(".request-put").click(function() {
            $.ajax({
                // https://stackoverflow.com/a/21201306
                url: $(this).attr("href"),
                method: "put",
                data: JSON.stringify({"book_data": $(this).attr("request-body")}),
                contentType: "application/json; charset=utf-8",
                success: function(response) {
                    alert(JSON.stringify(response));
                    location.reload();
                }
            });
        });
    });

});