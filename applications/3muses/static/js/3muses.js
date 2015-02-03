
//Let's get ready to rumble
$(document).ready(function(){

    //alert("1");


    $("input[name='address']").click(function(){


        // This is the id of the address that is to become the default
        // if it isn't a number, than don't do anything (not implemented yet)
        default_address_id=$(this).attr('value');

        // first ajax call is to get the value of the old default address id
        // from the session
        $.ajax({
            type:"POST",
            url:"get_current_default_address_id.html",
            data:{dummy_var: "dummy_var"}
        }).done(function( msg_daid ){
            // msg_daid should be the value of the old default address id
            // check to see if they are not the same
            // because if they are you don't do anything
            if (default_address_id!=msg_daid){
            
                // if they aren't let the user know we are preparing to generate the costs
                $('#shipping_target').html( "Preparing to generate shipping costs." );

                // start another ajax call to generate a more specific waiting message
                $.ajax({

                  type: "POST",
                  url: "loading_data.html",
                  data: { waiting_for: "easypost" },

                }).done(function( msg ) {
                    
                    // message will be generating shipping costs please wait

                    $('#shipping_target').html( msg );


                    // now that all those other checks are out of the way
                    // make a final ajax call that actually gets the shipping costs
                    $.ajax({

                        type: "POST",
                        url: "default_address.html",
                        data: { default_address_id: default_address_id},

                    }).done(function( shipping_grid ) {

                            $('#shipping_target').html( shipping_grid );

                    }); // end function on third ajax call

                }); // end function on second ajax call

            }; // end the if statement

        }); //End first function on first ajax call

    }); // End function on the onclick event


    // I need to add to this function to grey out the checkout button
    // until this is finished running
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
