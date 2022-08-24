var times = 0;
var random = Math.round(Math.random()*10)+4;

$('.verification-delete').click(function(){
        times+=1;
        document.getElementById("random").innerHTML="剩余"+(random-times)+"次";  
        
        if(times==random){
            $('.ui.tiny.modal.verification')
            .modal({
            closable  : true,
            onDeny    : function(){
                return true;
            },
            onApprove : function() {
                document.getElementById("button").removeAttribute("disabled");
            },
            })
            .modal('show');
        }else{
            document.getElementById("button").addAttribute("disabled");
        }
        
});

$('.agreement-show').click(function(){
     
    $('.ui.basic.modal.agreement')
    .modal({
      closable  : true,
      onDeny    : function(){
        document.getElementById("agreement").checked = false;
        return true;
      },
      onApprove : function() {
        document.getElementById("agreement").checked = true;
        return true;
      },
    })
    .modal('show');
});

//$(document)
//    .ready(function() {
//      $('.ui.form')
//        .form({
//          fields: {
//            username: {
//              identifier  : 'username',
//              rules: [
//                {
//                  type   : 'empty',
//                  prompt : '请输入用户名'
//                },
//                {
//                  type   : 'empty',
//                  prompt : '用户名不能为空'
//                }
//              ]
//            },
//            password: {
//              identifier  : 'password',
//              rules: [
//                {
//                  type   : 'empty',
//                  prompt : '请输入密码'
//                },
//                {
//                  type   : 'length[6]',
//                  prompt : '密码必须六位数以上'
//                }
//              ]
//            }
//          }
//        })
//      ;
//    })
//  ;