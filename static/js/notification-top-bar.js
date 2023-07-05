function get_latest_system_notification(url) {
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            if (!data.content) {
                return;
            }
            // $(".notification-top-bar-container").css("height", "40px");
            
            $(".notification-top-bar p").html(data.content);
            const background_color = data.category === "hint" ? "#1ABC9C" : "#FF6347";
            $(".notification-top-bar").css("background", background_color);
            $(".notification-top-bar").css("z-index", "9999");
            $(".notification-top-bar").fadeIn(500);
            // $('.ui.menu').fadeIn(0);
            $('.ui.container').fadeIn(500);
            $('.ui.footer').fadeIn(1000);
        }
    });
}