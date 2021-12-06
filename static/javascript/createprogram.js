$(document).ready(function(){

    $('form').on('submit', function(event){

        $.ajax({
            data: {
                dbname : $('#dbInput').val()
            },
            type: 'POST',
            url: '/programcreated'
        })
        .done(function(data) {

            if(data.error) {
                $('#errorAlert').text(data.Error).show();
                $('#successAlert').hide();
            }
            else{
                $('#successAlert').text(data.dbname).show();
                $('#errorAlert').hide();
            }
        });

        event.preventDefault();
    });

});
