

/*Variable Declarations*/
var DEFAULT_CHOICE='Choice1';

/*Functions*/

function update_target(click_class_name_or_all, selected_class_name, view_name, target_div_id){
    /*Get current selection is one exists first*/
    
    // alert("test");

    // alert('expected arguments are');
    // alert(update_target.length);

    // alert('passed arguments are');
    // alert(arguments.length);

    // alert(update_target.arguments[0].data)

    // for (x in update_target.arguments[0].data){
    //     alert(x);
    // }

    // Depending on how the function is called it handles the arguments differently, why!?
    if (arguments.length==1) {
        click_class_name=update_target.arguments[0].data['click_class_name'];
        selected_class_name=update_target.arguments[0].data['selected_class_name'];
        view_name=update_target.arguments[0].data['view_name'];
        target_div_id=update_target.arguments[0].data['target_div_id'];
    } else {
        click_class_name=click_class_name_or_all;
    };

    // This will be the db id of the address in the db table
    var new_choice=$(this).attr('id');
    // alert(new_choice);
    //var address_id=$(this).find('input[type=radio]').attr('value')

    // Find and check the radio button inside the clicked div
    var radButton = $(this).find('input[type=radio]');
    $(radButton).prop("checked", true);

    // remove selected class from all in group. Safer I think than just removing it from the one that has it
    $("."+click_class_name).removeClass( selected_class_name );

    // add the selected class to the clicked div. 
    $(this).addClass( selected_class_name );
    

    // Call ajax to sort some stuff out!
    $.ajax({

            type:"POST",
            url:view_name,
            data:{new_choice: new_choice},
            //async:false,

        }).done(function( shipping_information ){
            
            var obj=jQuery.parseJSON(shipping_information);

            /*This is not page load*/
            // if ( ($("#"+target_div_id).html()=="") || (obj.change==true) ) {

            //     $("#"+target_div_id).html( target_div_text );

            // }; 

            // alert(obj['shipping_options_LOD']);

            // if ( obj['error_status']=true ) {

            //     $("#"+"shipping_target").html( obj['error_message'] );

            // } else {

            //     $("#"+"shipping_target").html( obj['shipping_options_LOD'] );

            // };

            $("#"+"shipping_target").html( shipping_information );
            
            

        }).error( function (error_message) {
            alert(error_message['error'])});
};

/*This is for page load, ask the server what the current choice is, if there isn't one
default to Choice1*/

function set_selected_class2(session_var, selected_class_name, default_choice_id){
    
    //alert(session_var);
    //alert(selected_class_name);
    //alert(default_choice_id);

    $.ajax({

            type:"POST",
            url:'get_session_var.html',
            data: {session_var:session_var},
            /*async because it needs to know the choice before other stuff can happen*/
            async:false,

        }).done(function( variable ){

            alert(variable);

            if (variable!='None'){

                $('#'+variable).addClass( selected_class_name );

                var radButton = $('#'+variable).find('input[type=radio]');

                $(radButton).prop("checked", true);

            } else {

                $( '#'+default_choice_id ).addClass( selected_class_name );

                var radButton = $( '#'+default_choice_id ).find('input[type=radio]');

                $(radButton).prop("checked", true);

            };
            
        });
};


function get_default_address_id(selected_class_name){
    
    //alert(session_var);
    //alert(selected_class_name);
    //alert(default_choice_id);

    $.ajax({

            type:"POST",
            url:'get_default_address_id.html',
            //data: {session_var:session_var},
            /*async because it needs to know the choice before other stuff can happen*/
            async:false,

        }).done(function( variable ){

            alert(variable);

            return variable;
            
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



// for addresses in the cart

    var current_address_id=$('.selected_address').attr('id');

    $(".cart_address_info").on('click',{
        click_class_name:"cart_address_info", 
        selected_class_name:"selected_address", 
        view_name:"default_address.html",
        target_div_id:"shipping_target",
    }, update_target );

    $('#'+current_address_id).trigger('click');















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

    // To stop the carousels from sliding, only works on some pages for whatever reason
    //$('.carousel').carousel({interval:false});
    $(document).on('mouseleave', '.carousel', function() {$(this).carousel('pause');});
    
    //alert("3");

    $('.web2py_htmltable table').addClass('table-bordered');
    $('.web2py_htmltable table').addClass('muses_cart_table');

    //alert("4");

    $('.w2p_export_menu a').removeClass('btn-default');
    $('.w2p_export_menu a').addClass('btn-primary');

    // alert("5");

    $(".cart_grid_table_cell:contains(is no longer available)").addClass("cart_item_removed")

    //alert("6");

});
