/*
$(document).ready(function(){
  $("input[name='address']").click(function(){
    alert("clicked");
  });
});
*/


$(document).ready(function(){

    //alert("1");

    $("input[name='address']").click(function(){

        //alert("Clicked");

        default_address_id=$(this).attr('value');
        $('#shipping_target').html( "Preparing to generate shipping costs." );

        $.ajax({

          type: "POST",
          url: "loading_data.html",
          data: { waiting_for: "easypost" },

        }).done(function( msg ) {
            
            //alert( msg );

            $('#shipping_target').html( msg );

            //alert(default_address_id);

            $.ajax({

                type: "POST",
                url: "default_address.html",
                data: { default_address_id: default_address_id},

            }).done(function( shipping_grid ) {

                    $('#shipping_target').html( shipping_grid );

            });

        });

    });


    /*

        $("input[name='address']").click(function(){
        //alert($(this).attr('value'));

        $.ajax({
          type: "POST",
          url: "default_address.html",
          data: { default_address_id: $(this).attr('value')}
        })
          .done(function( shipping_grid ) {
            //alert( shipping_grid );
            $('#shipping_target').html( shipping_grid );
          });

    });

*/

    $("input[name='shipping']").click(function(){
       
        shipping_choice=$(this).attr('value');
        //alert(shipping_choice);

        $.ajax({

            type: "POST",
            url: "add_shipping_choice_to_session.html",
            data: { shipping_choice: shipping_choice }

        })
            .done(function( result ){
                //alert( "added to sesh" );
                result=jQuery.parseJSON(result)
                //alert( result.shipping_choice )
            });

    });



    $("input[name='card']").click(function(){
        //alert($(this).attr('value'));
        $.ajax({
            type: "POST",
            url: "default_card.html",
            data: { stripe_next_card_id: $(this).attr('value')}
        })
            .done(function( msg ){
                //alert( "Function Called");
            });

    });




    //alert("2");

/*    $('.carousel').carousel({interval:false});

    alert("3");*/
    
    $('.web2py_htmltable table').addClass('table-bordered');
    $('.web2py_htmltable table').addClass('muses_cart_table');

    //alert("4");

    $('.w2p_export_menu a').removeClass('btn-default');
    $('.w2p_export_menu a').addClass('btn-primary');

    // alert("5");








});
