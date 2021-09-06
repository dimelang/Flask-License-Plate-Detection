$(document).ready(function () {
    var cameraType = null;

    $.ajax({
        type: "GET",
        url: "/_load_model",
        contentType:'application/json',
        data: JSON.stringify({check:"Check"}),
        dataType: "json",
        success: function (response) {
            if (response=='Not Loaded'){
                $('#loadModel').modal('show')
                $.ajax({
                    type: "POST",
                    contentType:'application/json',
                    url: "/_load_model",
                    data: JSON.stringify({check:"Check"}),
                    dataType: "json",
                    success: function (response) {
                        window.location.href = response.redirect
                    }
                });
            }else{
                $('#loadModel').modal('hide')
            }
        }
    });
    
    
    // $('#videButton').find('button').not('#listVideo').each(function(){
    //     $(this).attr('disabled', 'disabled');
    // })


    $('#submitVideo').click(function (e) { 
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: "POST",
            url: "/_upload",
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (response) {
                $('#videoContainer').empty();
                window.location.href = response.redirect
                $('#videButton').find('button').each(function(){
                    $(this).removeAttr('disabled','disabled');
                })
            }
        });
        e.preventDefault();
        
    });

    $('#select-camera').change(function (e) { 
        cameraType = $('#select-camera option:selected').text();
        if (cameraType == 'CCTV') {
            var ipv4_address = $('input[name="ip"]');
            ipv4_address.inputmask({
                alias: "ip",
                greedy: false //The initial mask shown will be "" instead of "-____".
            });
        }
        e.preventDefault();
    });

    $('#webcam').click(function (e) { 
        var data = {file:cameraType};
        $.ajax({
            type: "POST",
            contentType:'application/json',
            url: "/_selected",
            data: JSON.stringify(data),
            dataType: "json",
            success: function (response) {
                $('#videoContainer').empty();
                console.log("Sukses");
                window.location.href = response.redirect
                $('#videButton').find('button').each(function(){
                    $(this).removeAttr('disabled','disabled');
                })
            }
        });
        e.preventDefault();
        
    });

    $('#stop').click(function (e) { 
        var data = {task:'Stop'};
        $.ajax({
            type: "POST",
            contentType:'application/json',
            url: "/_task",
            data: JSON.stringify(data),
            dataType: "json",
            success: function (response) {
                window.location.href = response.redirect
            }
        });
        e.preventDefault();
        
    });

    $('#cctv').click(function (e) { 
        var data = {file:cameraType,username:$('input[name="username"]').val(),pass:$('input[name="password"]').val(),ip:$('input[name="ip"]').val()};
        if ((data['name'] == "") || (data['pass']=="") || (data['ip']=="")){
            $("#selectedAssets").show();
        }else{
            $.ajax({
                type: "POST",
                contentType:'application/json',
                url: "/_selected",
                data: JSON.stringify(data),
                dataType: "json",
                success: function (response) {
                    $('#videoContainer').empty();
                    console.log("Sukses");
                    window.location.href = response.redirect
                    $('#videButton').find('button').each(function(){
                        $(this).removeAttr('disabled','disabled');
                    })
                    
                }
            });
        }
        e.preventDefault();
        
    });


    $('#listVideo').click(function (e) { 
        $.ajax({
            type: "POST",
            url: "/_listVideo",
            success: function (response) {
                $('#list').empty();
                for (let i=0;i<response.length;i++){
                    $('#list').append('<a href="#" class="list-group-item list-group-item-action">'+ response[i] +'</a>')
                }
            }
        });

        $('#mySidenav').attr('style', 'width:50%');
        // $('#main').attr('style', 'width:70vw');
        $('#main').attr('style', 'margin-left:25vw');


        e.preventDefault();
        
    });

    $('#list').click(function (e) { 
        // console.log($(this).text());
        $('#mySidenav').attr('style', 'width:0');
        $('#main').attr('style', 'margin-left:0'); 

        var data = {file: e.target.text};
        $.ajax({
            type: "POST",
            contentType:'application/json',
            url: "/_selected",
            data: JSON.stringify(data),
            dataType: "json",
            success: function (response) {
                $('#videoContainer').empty();
                console.log("Sukses");
                window.location.href = response.redirect
                $('#videButton').find('button').each(function(){
                    $(this).removeAttr('disabled','disabled');
                })
            }
        });
        e.preventDefault();
        
    });

    $('#close').click(function (e) { 
        $('#mySidenav').attr('style', 'width:0');
        $('#main').attr('style', 'margin-left:0'); 
        e.preventDefault();
        
    });

    $('#closeAlert1').on('click', function() {
        $("#selectedAssets").slideUp(500);
      });


    
    // $('a#calculate').click(function (e) { 
    //     var data = {a:$('input[name="a"]').val(),b:$('input[name="b"]').val()};

    //     $.ajax({
    //         type: "POST",
    //         contentType:'application/json',
    //         url: "/_add_numbers",
    //         data: JSON.stringify(data),
    //         dataType: "json",
    //         success: function (response) {
    //             console.log('Result');
    //             console.log(response);
    //             $('#result').text(response);
                
    //         }
    //     });
    //     e.preventDefault();
        
    // });

    $('#cctvConfig').hide();
    $('#webcam').hide();
    $('#select-camera').change(function (e) { 
        if ($(this).val()==1){
            $('#cctvConfig').hide();
            $('#webcam').show();
        }else if ($(this).val()==2){
            $('#cctvConfig').show();
            $('#webcam').hide();
        }else{
            $('#webcam').hide();
            $('#cctvConfig').hide();
        }
        e.preventDefault();
    });

    $('#showPass').click(function (e) { 
        if ($('#password').attr('type')=='text'){
            $('#password').attr('type', 'password');
            $('#showPass i').addClass("fa-eye-slash");
            $('#showPass i').removeClass( "fa-eye" );
        }else if($('#password').attr('type')=='password'){
            $('#password').attr('type', 'text');
            $('#showPass i').removeClass( "fa-eye-slash" );
            $('#showPass i').addClass("fa-eye");
        }
        
        e.preventDefault();  
    });

    
});