

/*Variable Declarations*/
var DEFAULT_CHOICE='Choice1';

/*Functions*/

function update_target(click_class_name_or_all, selected_class_name, view_name, target_div_id){

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


            var newHtml=[]

            if ( obj['error_status']===true ) {

                newHtml.push('<div class="row cart-view-shipping-row">');
                     newHtml.push('<div class="col-md-offset-2 col-md-8 cart-view-shipping-row-error">')

                         newHtml.push(obj['error_message']);

                     newHtml.push('</div>');
                 newHtml.push('</div>');

                 target_html=newHtml.join('');

                 //$("#"+"shipping_target").html( '<div class="col-md-offset-2 col-md-8">' + obj['error_message'] + '</div>');

                 $("#"+"shipping_target").html( target_html );

                 //$("#"+"shipping_target").html( obj['error_message'] );

             } else {

                //alert(obj['shipping_options_LOD'].length);
                //alert(obj['shipping_options_LOD'][0]['rate_id']);

                for (i=obj['shipping_options_LOD'].length-1;i>=0;i--){

                    newHtml.push('<div class="row cart-view-shipping-row">');


                        newHtml.push('<div class="row col-xs-8 col-md-offset-2 col-md-5 cart-view-shipping-row-subset">');


                            newHtml.push('<div class="col-md-5 vert-hori-center-parent">');
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push(obj['shipping_options_LOD'][i]['carrier']);
                                newHtml.push('</div>');
                            newHtml.push('</div>');


                            newHtml.push('<div class="col-md-7">')
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push(obj['shipping_options_LOD'][i]['service']);
                                newHtml.push('</div>');
                            newHtml.push('</div>');


                        newHtml.push('</div>');


                        newHtml.push('<div class="row col-xs-5 col-md-3 cart-view-shipping-row-subset">');

                            newHtml.push('<div class="col-md-4">')
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push(obj['shipping_options_LOD'][i]['rate']);
                                newHtml.push('</div>');
                            newHtml.push('</div>');


                            newHtml.push('<div class="col-md-8">')
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push(obj['shipping_options_LOD'][i]['delivery_days']);
                                newHtml.push('</div>');
                            newHtml.push('</div>');

                        newHtml.push('</div>');


                    newHtml.push('</div>');
                    newHtml.push('<br/>');                          
                         
                };
                    
                target_html=newHtml.join('');

                $("#"+"shipping_target").html( target_html );
                //$("#"+"shipping_target").html( shipping_information );

             };

            
        }).error( function (error_message) {
            alert( "Help, I need an adult!" )});
};


//Let's get ready to rumble
$(document).ready(function(){


    // Add classes to auth

    $("#auth_user_email").addClass("form-control");
    $("#auth_user_password").addClass("form-control");
    $("#auth_user_remember").addClass("display_inline_block_class");
    $("input[value=Login]").addClass("form-control btn-success");
    $("#auth_user_email__label").addClass("display_none_class");
    $("#auth_user_password__label").addClass("display_none_class");





// for addresses in the cart

    $('input[type=radio]:checked').parent().addClass('selected_address');

    var current_address_id=$('.selected_address').attr('id');
    // alert(current_address_id);
    // alert(current_address_id);

    $(".cart-view-address-info").on('click',{
        click_class_name:"cart-view-address-info", 
        selected_class_name:"selected_address", 
        view_name:"ajax_shipping_information.html",
        target_div_id:"shipping_target",
    }, update_target );

    $('#'+current_address_id).trigger('click');



// for shipping options in the cart

    $(".cart-view-shipping-row-subset").on("click", function(){
        alert("The paragraph was clicked.");
    });







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

    $(function () {
      $('[data-toggle="popover"]').popover()
    })


    // $(function() {
    //     var pop = $('.popbtn');
    //     // var pop = $('[data-toggle="popover"]')
    //     // var row = $('.row:not(:first):not(:last)');
    //     // var row = $('.cart-view-cart-row');

    //     pop.popover({
    //         trigger: 'manual',
    //         html: true,
    //         container: 'body',
    //         placement: 'bottom',
    //         animation: false,
    //         content: function() {
    //             return $('#popover').html();
    //         }
    //     });


    //     pop.on('click', function(e) {
    //         pop.popover('toggle');
    //         pop.not(this).popover('hide');
    //     });

    //     $(window).on('resize', function() {
    //         pop.popover('hide');
    //     });

    //     // row.on('touchend', function(e) {
    //     //     $(this).find('.popbtn').popover('toggle');
    //     //     row.not(this).find('.popbtn').popover('hide');
    //     //     return false;
    //     // });

    // });





});
