/*
UNUSED FUNCTIONS

function get_info_from_server(view_html){
    var current_choice
    var previous_choice
    $.ajax({
        type:"POST",
        url:view_html,

    }).done(function(data_dict){
        current_choice=data_dict['current_choice'];
    })
};

*/

/*Variable Declarations*/
var DEFAULT_CHOICE='Choice1';

/*Functions*/

/*
For scratch.html currently
*/

function update_target(click_class_name, selected_class_name, view_name, target_div_id){
    /*Get current selection is one exists first*/
    var new_choice=$(this).attr('id')

    $(".scratch_div").removeClass('selected');

    $(this).addClass( "selected" );

    $.ajax({

            type:"POST",
            url:"scratch_ajax.html",
            data:{new_choice: new_choice}

        }).done(function( target_div_text ){
            
            var obj=jQuery.parseJSON(target_div_text);

            /*This is not page load*/
            if ( ($("#scratch_target").html()=="") || (obj.change==true) ) {

                $("#scratch_target").html( target_div_text );

            }; 

        });
};

/*
For scratch.html currently
This is for page load, ask the server what the current choice is, if there isn't one
default to Choice1*/

function set_selected_class2(session_var, selected_class_name, default_choice_id){
    $.ajax({

            type:"POST",
            url:'get_session_var.html',
            data: {session_var:session_var},
            /*async because it needs to know the choice before other stuff can happen*/
            async:false,

        }).done(function( variable ){

            if (variable!='None'){

                $('#'+variable).addClass( selected_class_name );

            } else {

                /*Choice1 should probably be a variable declared earlier like DEFAULT_CHOICE*/
                $( '#'+default_choice_id ).addClass( selected_class_name );

            };
            
        });
};


//Let's get ready to rumble
$(document).ready(function(){

    /*ask server for current choice in session*/

    if (window.location.pathname == '/scratch'){
        //set_selected_class();
        set_selected_class2('current_choice', 'selected', DEFAULT_CHOICE);
    }

    var current_id=$('.selected').attr('id');

    //$(".scratch_div").on('click',update_target);

    $(".scratch_div").on('click',{
        click_class_name:"scratch_div", 
        selected_class_name:"selected", 
        view_name:"scratch_ajax.html",
        target_div_id:"scratch_target",
    }, update_target );

    
    $('#'+current_id).trigger('click');



    $(".cart_grid_table_cell:contains(is no longer available)").addClass("cart_item_removed")

// removed because redundancy
    /*$("input[name='address']").click(function(){
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
*/

/*
    $(".cart_address_container").click(function(){
        alert("clicked");
        var radButton = $(this).find('input[type=radio]');
        $(radButton).prop("checked", true);
        default_address_id=$(radButton).attr('value');
        alert(default_address_id);

        $.ajax({
            type:"POST",
            url:"get_current_default_address_id.html",
            data:{dummy_var: "dummy_var"}
        }).done(function( msg_daid ) {

            alert(default_address_id);
            alert(msg_daid);


            if (default_address_id!=msg_daid){
            
                // if they aren't let the user know we are preparing to generate the costs
                $('#shipping_target').html( "Preparing to generate shipping costs." );


                $.ajax({
                    type:"POST",
                    url:"update_default_address.html",
                    data:{default_address_id:default_address_id},
                }).done(function( yay ) {

                    alert(yay);

                }); // second ajax call

            }; // end if

        }); // first ajax call

    }); // address container click
*/


/*
When a user loads the cart page, the shipping costs should be retrieved using the currently selected default id
If there is no id selected, the page should tell the user they need to select an address before getting shipping info
If the user selects a new id, the shipping costs should update to reflect that change, with some kind of visual feedback for the user while the info is being retrieved
If the user selects an address that is already selected, nothing should happen.
If the user creates a new address, that should beome the default.
If the user edits an existing address, that should become the defualt. 
If the user deletes an address that is not the default, ajax should be used to delete the address without reloading the page
If the user deletes an address that is the default, if there is only one other address is should auto select that address, if there are multiple is should replace the shipping info with the message asking the user to select an address. all with ajax.
Editing the address should also be done inline.

*/
  
/*

//This function is sending bad http!
    $(".cart_address_container").click(function(){

        //Check the readio button because it keeps track of the id
        var radButton = $(this).find('input[type=radio]');
        $(radButton).prop("checked", true);

        // This is the id of the address that is to become the default
        default_address_id=$(radButton).attr('value');
        
        //alert(default_address_id);
        


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
            
            //alert(default_address_id);
            //alert(msg_daid);
            

            if (default_address_id!=msg_daid){
            
                // if they aren't let the user know we are preparing to generate the costs
                $('#shipping_target').html( "Preparing to generate shipping costs." );

                // start another ajax call that will set the current address so be know it's the default
                // involves updating the session variable, but also making defaut address in db True if logged in
                $.ajax({
                    type:"POST",
                    url:"update_default_address.html",
                    data:{default_address_id:default_address_id},
                }).done(function( yay ) {

                    //alert(yay);
                    
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

                        }); // end function on ajax call that gets shipping info

                    }); // end function on ajax call that generates a more specific waiting message

                }); // end function on ajax call that resets the default_address_id

            }; // end the if statement

        }); //End first function on first ajax call

    }); // End function on the onclick event

*/






    // I need to add to this function to grey out the checkout button
    // until this is finished running
    $("input[name='shipping']").click(function(){
        
        //alert('clicked');
        
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
