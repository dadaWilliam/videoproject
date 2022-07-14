
// 写入csrf
$.getScript("/static/js/csrftoken.js");

$('.advertising').click(function(){
      var tr = $(this).closest("tr");
      var video_id = $(tr).attr("video-id");
        $('.ui.tiny.modal.advertising')
        .modal({
          closable  : true,
          onDeny    : function(){
            return true;
          },
          onApprove : function() {

            $.ajax({
                url: api_advertising,
                data: {
                    'video_id':video_id,
                    'csrf_token': csrftoken
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                    console.log(data);
                     var code = data.code
                     var msg = data.msg
                     if(code == 0){ 
                        window.location.reload();
                     }else{
                        alert(msg);
                     }
                },
                error: function(data){
                  alert("error"+data)
                }
            });

          }
        })
        .modal('show');
});
