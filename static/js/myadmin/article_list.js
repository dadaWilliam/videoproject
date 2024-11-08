
// 写入csrf
$.getScript("/static/js/csrftoken.js");

$('.article-delete').click(function(){
      var tr = $(this).closest("tr");
      var article_id = $(tr).attr("article-id");
        $('.ui.tiny.modal.delete')
        .modal({
          closable  : true,
          onDeny    : function(){
            return true;
          },
          onApprove : function() {

            $.ajax({
                url: api_article_delete,
                data: {
                    'article_id':article_id,
                    'csrf_token': csrftoken
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                    console.log(data);
                     var code = data.code
                     if(code == 0){
                        window.location.reload();
                     }else{
                        alert(""+data.msg)
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


// search
$('#v-search').bind('keypress',function(event){
    var word = $('#v-search').val()
    if(event.keyCode == "13" && word.length > 0)
    {
        window.location = search_url + '?q='+word;
    }
});

$('#search').click(function(){
    var word = $('#v-search').val()
    if(word.length > 0){
        window.location = search_url + '?q='+word;
    }
})