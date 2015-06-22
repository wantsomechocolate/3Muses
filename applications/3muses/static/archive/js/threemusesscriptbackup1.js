
/*Variable Declarations*/


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
            async:true,

        }).done(function( shipping_information ){
            
            var obj=jQuery.parseJSON(shipping_information);

            // alert(obj);

            /*This is not page load*/
            // if ( ($("#"+target_div_id).html()=="") || (obj.change==true) ) {

            //     $("#"+target_div_id).html( target_div_text );

            // }; 

            // alert(obj['shipping_options_LOD']);
            // alert(obj['error_status']);
            // alert(obj['error_message']);


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

                newHtml.push('<div class="row cart-view-row cart-view-shipping-header">');
                    newHtml.push('<div class="col-md-offset-2 col-md-8 cart-view-shipping-header-2">');


                        newHtml.push('<div class="col-xs-7 col-md-7 cart-view-shipping-header-3">');

                            newHtml.push('<div class="col-md-5 vert-hori-center-parent">');
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push("Carrier");
                                newHtml.push('</div>');
                            newHtml.push('</div>');


                            newHtml.push('<div class="col-md-7">')
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push("Service Type");
                                newHtml.push('</div>');
                            newHtml.push('</div>');

                        newHtml.push('</div>');


                        newHtml.push('<div class="col-xs-5 col-md-5 cart-view-shipping-header-3">');

                            newHtml.push('<div class="col-md-4">')
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push("Rate");
                                newHtml.push('</div>');
                            newHtml.push('</div>');


                            newHtml.push('<div class="col-md-8">')
                                newHtml.push('<div class="vert-hori-center-child">');
                                    newHtml.push("Delivery Date*");
                                newHtml.push('</div>');
                            newHtml.push('</div>');

                        newHtml.push('</div>');


                    newHtml.push('</div>');
                newHtml.push('</div>');



                for (i=obj['shipping_options_LOD'].length-1;i>=0;i--){

                    //Try to get the upper bound estimated delivery date
                    delivery_days=obj['shipping_options_LOD'][i]['delivery_days'];

                    delivery_date = new Date();

                    if (delivery_days>0){
                        // alert("delivery days were 0")
                        delivery_date.setDate(delivery_date.getDate()+delivery_days);
                        formatted_date=moment(delivery_date).format('ddd MMM Do');
                    } else {
                        // alert("delivery days were something else, probably none")
                        // delivery_date.setDate(delivery_date.getDate()+5);
                        formatted_date='N/A'
                    };

                    // alert(delivery_date);
                    
                    // alert(formatted_date);
                    

                    newHtml.push('<div class="row cart-view-row cart-view-shipping-row">');

                        // alert(obj['shipping_options_LOD'][i]['selected_shipping_option']);

                        if (obj['shipping_options_LOD'][i]['selected_shipping_option']===true){

                            newHtml.push('<div class="col-md-offset-2 col-md-8 cart-view-shipping-row-wrapper cart-view-shipping-row-wrapper-selected" id="'+obj['shipping_options_LOD'][i]['rate_id']+'">');

                        } else {

                            newHtml.push('<div class="col-md-offset-2 col-md-8 cart-view-shipping-row-wrapper" id="'+obj['shipping_options_LOD'][i]['rate_id']+'">');

                        };
                        

                            newHtml.push('<div class="col-xs-7 col-md-7 cart-view-shipping-row-subset">');


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


                            newHtml.push('<div class="col-xs-5 col-md-5 cart-view-shipping-row-subset">');


                                newHtml.push('<div class="col-md-4">')
                                    newHtml.push('<div class="vert-hori-center-child">');
                                        newHtml.push("$"+obj['shipping_options_LOD'][i]['rate']);
                                    newHtml.push('</div>');
                                newHtml.push('</div>');


                                newHtml.push('<div class="col-md-8">')
                                    newHtml.push('<div class="vert-hori-center-child">');
                                        newHtml.push(formatted_date);
                                    newHtml.push('</div>');
                                newHtml.push('</div>');


                            newHtml.push('</div>');

                        newHtml.push('</div>');

                    newHtml.push('</div>');

                    newHtml.push('<br/>');                          
                         
                }; //For loop closing
                    
                target_html=newHtml.join('');

                $("#"+"shipping_target").html( target_html );

                var current_shipping_div_id=$('.cart-view-shipping-row-wrapper-selected').attr('id');
                $("#"+current_shipping_div_id).trigger('click');                

             }; // Should be the else closing

        // Closing the initial ajax call
        }).error( function (error_message) {
            // alert( "There was an error, your shipping option has not been set." )
            // alert(error_message);
            var newHtml=[]

            newHtml.push('<div class="row cart-view-shipping-row">');
                 newHtml.push('<div class="col-md-offset-2 col-md-8 cart-view-shipping-row-error">')

                     newHtml.push("There was an error retrieving the shipping information. I should use estimates in this case!");

                 newHtml.push('</div>');
             newHtml.push('</div>');

             target_html=newHtml.join('');

             $("#"+target_div_id).html( target_html );





        }); // Close the error clause of the ajax call

}; // Closes the function


function update_shipping_option(value_one_or_all, value_two){

    // Depending on how the function is called it handles the arguments differently, why!?
    if (arguments.length==1) {
        value_one=update_shipping_option.arguments[0].data['value_one'];
        value_two=update_shipping_option.arguments[0].data['value_two'];
    } else {
        value_one=value_one_or_all;
    };

    // alert(value_two);

    $(".cart-view-shipping-row-wrapper").removeClass('cart-view-shipping-row-wrapper-selected');
    $(this).addClass("cart-view-shipping-row-wrapper-selected");

    shipping_choice_rate_id=$(this).attr('id');

    // alert(shipping_choice_rate_id);

 // Call ajax to sort some stuff out!
    $.ajax({

            type:"POST",
            url:"ajax_choose_shipping_option.html",
            data:{shipping_choice_rate_id: shipping_choice_rate_id},
            // async=false,

        }).done(function( obj_json ){

            var obj=jQuery.parseJSON( obj_json );
            // alert(obj['shipping_cost_USD'])
            $("#cart-view-summary-shipping-cost-div").html( "$"+obj['shipping_cost_USD'] );
            $("#cart-view-summary-total-cost-div").html( "$"+obj['total_cost_USD'] );


            // alert( obj['msg'] );

        }).error( function (error_message) {
            alert( "There was an error setting your shipping option in the db" )});

};


function update_payment_option(value_one_or_all, value_two){

    // Depending on how the function is called it handles the arguments differently, why!?
    if (arguments.length==1) {
        value_one=update_payment_option.arguments[0].data['value_one'];
        value_two=update_payment_option.arguments[0].data['value_two'];
    } else {
        value_one=value_one_or_all;
    };

    // alert("a payment option has been clicked");

    $(".cart-view-payment-option").removeClass("cart-view-payment-option-selected");
    $(this).addClass("cart-view-payment-option-selected");

    payment_method=$(this).attr('id');

    $.ajax({

            type:"POST",
            url:"ajax_choose_payment_option.html",
            data:{payment_method: payment_method},

        }).done(function( obj_json ){

            // var obj=jQuery.parseJSON( obj_json );

            // alert( obj['msg'] );

            // alert("Success!");

        }).error( function (error_message) {
            alert( "There was an error setting your shipping option in the db" )});

};





// function carouselNormalization() { //carousel_class) {

//     // carousel_class=carouselNormalization.arguments[0].data['carousel_class'];



//     // var items = $('.'+carousel_class+' .item'), //grab all slides
//     var items = $('.'+'display-carousel'+' .item'), //grab all slides
//         heights = [], //create empty array to store height values
//         tallest; //create variable to make note of the tallest slide

//     // var imgs = $('.'+carousel_class+' .item a img'),
//     var imgs = $('.'+'display-carousel'+' .item a img'),
//         img_heights = [];

//     function normalizeHeights() {

//         items.each(function() { //add heights to array
//             heights.push($(this).height()); 
//         });

//         tallest = Math.max.apply(null, heights); //cache largest value
//         items.each(function() {
//             $(this).css('min-height',tallest + 'px');
//         });

//         imgs.each(function(){
//             $(this).css('height', tallest + 'px');
//         })

//     };

//     normalizeHeights();

//     // $(window).on('resize orientationchange', function () {
//     //     tallest = 0, heights.length = 0; //reset vars
//     //     items.each(function() {
//     //         $(this).css('min-height','0'); //reset min-height
//     //     }); 
//     //     normalizeHeights(); //run it again 
//     // });
    
// }


// function adjust_slider_heights(){

//     var width=$('.display-carousel').width()*.9;

    // if (width==0){
        
    //     var width=$('.display-carousel').width()*.9;

    //     $('.slider-size').css({'height':width+"px !important"})

    // } else {

    // $('.slider-size').css({'height':width+"px"})

    // };


// }




function adjust_slider_heights(){

    var width=$('.carousel').width()*.9;
    // alert(width);
    // if (width==0){  
    //     var width=$('.display-carousel').width()*.9;
    //     // $('.slider-size').css({'height':width+"px !important"});
    //     adjust_slider_heights();
    // } else {
    $('.slider-size').css({'height':width+"px"})
    // };
};


$(window).on("resize", adjust_slider_heights);
$(window).on("load", adjust_slider_heights);
$(window).on("orientationchange", adjust_slider_heights);



function centerImageVertically() {
    var imgframes = $('.image-container a img');
    imgframes.each(function (i) {
        // var imgVRelativeOffset = ($(this).height() - $(this).parent(".image-container").height()) / 2;
        current_img_width=$(this).width();
        current_img_height=$(this).height();

        container_width=$(this).width(this).parent().parent().width();
        container_height=$(this).height(this).parent().parent().height();

        // $('#object').width($('#object').parent().width());

        // alert(current_img_width);
        // alert(current_img_height);
        // alert(container_width);
        // alert(container_height);
        // alert("s");
        img_ar=current_img_width/current_img_height;
        container_ar=container_width/container_height;

        // alert(img_ar);
        // alert(container_ar);
        // alert("1");
        if (img_ar>container_ar){
            // alert("2");
            img_min_width_px=img_ar*container_height;

        } else if (img_ar<container_ar) {
            // alert("3");
            img_min_width_px=container_width;

        } else {
            // alert("4");
            img_min_width_px=current_img_width;

        };
        // alert(img_min_width_px);
        $(this).css({
            'min-width':img_min_width_px+'px'
        });
    });
};


// centerImageVertically();
// $(window).resize(centerImageVertically);
$(window).on("resize", centerImageVertically);
$(window).on("load", centerImageVertically);
$(window).on("orientationchange", centerImageVertically);


//Let's get ready to rumble
$(document).ready(function(){


    // alert(moment().format());


    // var center_fill = function (){

    //     var img_frames = $('.image-container a img');
    //      img_frames.each(function(){

    //         current_img_width=parseInt($(this).css('width'));
    //         current_img_height=parseInt($(this).css('height'));










    //      });
    // };



// http://stackoverflow.com/questions/17084246/make-image-fill-div-proportionally-and-center-image-vertically

    //Enable swiping...
    $(".carousel-inner").swipe( {
        //Generic swipe handler for all directions
        swipeLeft:function(event, direction, distance, duration, fingerCount) {
            $(this).parent().carousel('next'); 
        },
        swipeRight: function() {
            $(this).parent().carousel('prev'); 
        },
        //Default is 75px, set to 0 for demo so any distance triggers swipe
        threshold:10
    });


    // var width=$('.slider-size').width()*.9;
    // // alert(width);

    // $('.slider-size').css('height',width+"px")









// find the height and width of each image and the height and width of each parent
// if the aspect ratio w/h of the img is higher than the container
// that means you will need to adjust the height and let the width overflow
// if the aspect ratio w/h of the img is lower than the container
// The width expands to fill the container, and the vertically positioning needs to be adjusted so that the image is centered



    



    // $(".frame img").centerImage();


    // Add classes to auth

    var current_page=window.location.pathname;
    // alert(current_page);

    if (current_page==='/user/register'){

        $("input[type=submit]").addClass("btn-info");

        $("input[name=first_name]").attr("placeholder", "First Name");
        $("input[name=last_name]").attr("placeholder", "Last Name");
        $("input[name=email]").attr("placeholder", "Email Address");
        $("input[name=password]").attr("placeholder", "Password");
        $("input[name=password_two]").attr("placeholder", "Verify Password");

    } else if (current_page==='/user/login'||current_page==='/default/user/login'){

        $("input[type=submit]").addClass("btn-info");
        $("input[type=text]").attr("placeholder", "Enter Your Email Address");
        $("input[type=password]").attr("placeholder", "Enter Your Password");

    } else if (current_page==='/user/request_reset_password'){

        $("input[type=submit]").addClass("btn-info");
        $("input[name=email]").attr("placeholder", "Enter Your Email Address");

    } else if (current_page==='/user/profile'||current_page==='/default/user/profile'){

        $("input[type=submit]").addClass("btn-info");
        // $("input[name=email]").attr("placeholder", "Enter Your Email Address");

    };



    // alert(current_page);

    // if (current_page==='user/login'){

    //     $("#auth_user_email").addClass("form-control");
    //     $("#auth_user_password").addClass("form-control");
    //     $("#auth_user_remember").addClass("display_inline_block_class");
    //     $("input[value=Login]").addClass("form-control btn-success");
    //     $("#auth_user_email__label").addClass("display_none_class");
    //     $("#auth_user_password__label").addClass("display_none_class");

    // };





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

    // $(".cart-view-shipping-row-wrapper").on('click',{
    //     value_one:"value",
    //     value_two:"value",
    // }, update_shipping_option );

    // $(document).on("click",".cart-view-shipping-row-wrapper",function(e){
    //     alert("I've been clicked"); 
    // });

    $(document).on("click",".cart-view-shipping-row-wrapper",{
        value_one:"value one",
        value_two:"value two",
    }, update_shipping_option );

    // $('.cart-view-shipping-row-wrapper').on("click",{
    //     value_one:"value one",
    //     value_two:"value two",
    // }, update_shipping_option );

    var current_shipping_div_id=$('.cart-view-shipping-row-wrapper-selected').attr('id');
    $("#"+current_shipping_div_id).trigger('click');




    $(document).on("click",".cart-view-payment-option",{
        value_one:"value one",
        value_two:"value two",
    }, update_payment_option );




    // // I need to add to this function to grey out the checkout button
    // // until this is finished running
    // $("input[name='shipping']").click(function(){
    //     //alert('clicked');
    //     shipping_choice=$(this).attr('value');
    //     //alert(shipping_choice);
    //     $.ajax({
    //         type: "POST",
    //         url: "add_shipping_choice_to_session.html",
    //         data: { shipping_choice: shipping_choice }
    //     })
    //         .done(function( result ){
    //             //alert( "added to sesh" );
    //             result=jQuery.parseJSON(result)
    //             //alert( result.shipping_choice )
    //         });
    // });





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
    $('.web2py_htmltable table').addClass('manage-view-table');

    //alert("4");

    $('.w2p_export_menu a').removeClass('btn-default');
    $('.w2p_export_menu a').addClass('btn-primary');

    // alert("5");

    $(".cart_grid_table_cell:contains(is no longer available)").addClass("cart_item_removed")

    //alert("6");

    $(function () {
      $('[data-toggle="popover"]').popover()
    })


    // $("#demo01").animatedModal();


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



    // $(window).on("load resize orientationchange", carouselNormalization)

    // carouselNormalization('display-carousel');


    // $(document).on("ready resize orientationchange",".display-carousel",{

    //     carousel_class:"display-carousel",
        
    // }, carouselNormalization );


    // $("#display-carousel-0").swiperight(function() {  
    //     $(this).carousel('prev');  
    // });  

    // $("#display-carousel-0").swipeleft(function() {  
    //     $(this).carousel('next');  
    // });  



  var flashBox = jQuery(".flash"), flashTimer;
  flashBox.click(function(){
      if (flashTimer) clearTimeout(flashTimer);
      flashBox.fadeOut(400, function(){jQuery(".flash").html('')});
  });
  flashTimer = setTimeout(function(){flashBox.fadeOut(400, function(){jQuery(".flash").html('')});}, 3500);


/*Make this conditional for the confirmation page*/
$("#confirmation input[name=old_password]").val("guestuser");

// $("#confirmation input[name=first_name").val("");
// $("#confirmation input[name=last_name").val("");
$("#confirmation input[name=email").val("");


// $("#confirmation input[name=first_name]").attr("placeholder", "Enter First Name");
// $("#confirmation input[name=last_name]").attr("placeholder", "Enter Last Name");
$("#confirmation input[name=email]").attr("placeholder", "Enter Email");

// $("#confirmation input[name=new_password]").attr("placeholder", "Enter Password");
// $("#confirmation input[name=new_password2]").attr("placeholder", "Verify Password");

});
