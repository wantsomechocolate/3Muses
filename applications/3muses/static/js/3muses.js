
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


    // Give the user some sweet feedback
    $("#"+target_div_id).html( '<div class="row cart-view-row cart-view-shipping-row"><div class="col-md-offset-2 col-md-8 align-hcenter cart-view-error-text-container"> Generating Shipping Costs... Please Wait <img src="static/img/bouncing_ball_0099CC.gif" style="width: 20px;"> </div></div>'
    );


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

    $("#cart-view-summary-shipping-cost-div").html( '<img src="static/img/squares_transparent.gif" style="width: 20px;">' );
    $("#cart-view-summary-total-cost-div").html( '<img src="static/img/squares_transparent.gif" style="width: 20px;">' );

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

            $('#cart-to-checkout').prop('disabled', false);
            // alert( obj['msg'] );

        }).error( function (error_message) {
            alert( "There was an error setting your shipping option in the db" )});

};


// function update_payment_option(value_one_or_all, value_two){

//     // Depending on how the function is called it handles the arguments differently, why!?
//     if (arguments.length==1) {
//         value_one=update_payment_option.arguments[0].data['value_one'];
//         value_two=update_payment_option.arguments[0].data['value_two'];
//     } else {
//         value_one=value_one_or_all;
//     };

//     // alert("a payment option has been clicked");

//     $(".cart-view-payment-option").removeClass("cart-view-payment-option-selected");
//     $(this).addClass("cart-view-payment-option-selected");

//     payment_method=$(this).attr('id');

//     $.ajax({

//             type:"POST",
//             url:"ajax_choose_payment_option.html",
//             data:{payment_method: payment_method},

//         }).done(function( obj_json ){

//             // var obj=jQuery.parseJSON( obj_json );
//             // alert( obj['msg'] );
//             // alert("Success!");

//         }).error( function (error_message) {
//             alert( "There was an error setting your shipping option in the db" )});

// };




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


function adjust_slider_heights(){

    page_name=window.location.pathname.split('/')[1];

    if (page_name=="display"||page_name=='product'){

        var width=$('.carousel').width()*0.85;
        $('.slider-size').css({'height':width+"px"})

    } else if (page_name=='categories'){
        var width=$('.slider-size').width()*0.9;
        $('.slider-size').css({'height':width+"px"})

    }

};



// http://stackoverflow.com/questions/17084246/make-image-fill-div-proportionally-and-center-image-vertically
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





// $(document).on("click",".cart-view-payment-option",{
//     value_one:"value one",
//     value_two:"value two",
// }, update_payment_option );


var $form = $('#payment-form');

var handler = StripeCheckout.configure({
    key: 'pk_test_pDkBiVWtEb6hIErKE13J9Ohr',
    // image: '/img/documentation/checkout/marketplace.png',
    // do this when a token is generated
    token: function(token) {


    isTokenCreated = true;

     // pop up with token id and email
     // prompt("Copy to clip board control c enter","?stripeToken="+token.id+"&stripeEmail="+token.email);
     // add token and email address to the form
     $form.append($('<input type="hidden" name="stripeToken" />').val(token.id));
     $form.append($('<input type="hidden" name="stripeEmail" />').val(token.email));
     
     // submit form, uncomment to make this happen
     $form.get(0).submit();
    },
    // do this when the window is opened
    opened:function() {
        // alert("You opened the checkout window");
    },
    // do this when the window is closed
    closed: function() {

         // alert("You closed the checkout window");

        // set timeout ensures that token can fire first on mobile
         setTimeout(function() {  
       
         if(isTokenCreated) {
           // alert("Checkout completed successfully!");
           isTokenCreated = false; // reset so you can checkout again?
           $('#please-wait-stripe-btn').click();
         } else {
           // alert("Didn't finish Checkout!");
            $('#please-wait-stripe-btn').click();                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
         }
         },100);

      }
  });


//Let's get ready to rumble
$(document).ready(function(){

    $('#customButton').on('click', function(e) {
        // Open Checkout with further options
        isTokenCreated=false;
        handler.open({

            name: 'ThreeMusesGlass',
            description: 'Purchase Details from ThreeMusesGlass',
            bitcoin:"true",
            zipCode: true,
            amount: 1018,
            // label:"Check out with Stripe",
            panelLabel:"Pay",
            image:"http://images.clipartpanda.com/smiley-face-png-1407-smiley-face.png",

        });

        e.preventDefault();

      });

        // 
     //Close Checkout on page navigation
      $(window).on('popstate', function() {

        handler.close();

      });







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
        threshold:0
    });

    // Stuff I want to do on things

    // resize images (not just in carousels though)
    $(window).on("resize", adjust_slider_heights);
    $(window).on("load", adjust_slider_heights);
    $(window).on("orientationchange", adjust_slider_heights);


    // center image vertically on these things and also one extra thing which is on carousel slide
    $(window).on("resize", centerImageVertically);
    $(window).on("load", centerImageVertically);
    $(window).on("orientationchange", centerImageVertically);
    $('.carousel').on('slide',centerImageVertically);





    // This is like my main function.
    $(document).on("click",".cart-view-shipping-row-wrapper",{
        value_one:"value one",
        value_two:"value two",
    }, update_shipping_option );




    // To stop the carousels from sliding, only works on some pages for whatever reason
    $(document).on('mouseleave', '.carousel', function() {$(this).carousel('pause');});




    // To enable popovers (but there aren't any to enable right now)

    $('[data-toggle="popover"]').popover()



    // To enable the flash messages without 
    var flashBox = jQuery(".flash"), flashTimer;
    flashBox.click(function(){
        if (flashTimer) clearTimeout(flashTimer);
        flashBox.fadeOut(400, function(){jQuery(".flash").html('')});
    });
    flashTimer = setTimeout(function(){flashBox.fadeOut(400, function(){jQuery(".flash").html('')});}, 3500);




    // for addresses in the cart
    // $('input[type=radio]:checked').parent().addClass('selected_address');

    var current_address_id=$('.selected_address').attr('id');

    // var current_address_id=111;

    $(".cart-view-address-info").on('click',{
        click_class_name:"cart-view-address-info", 
        selected_class_name:"selected_address", 
        view_name:"ajax_shipping_information.html",
        target_div_id:"shipping_target",
    }, update_target );

    $('#'+current_address_id).trigger('click');



    // This probably needs to be put in the success of the ajax call from the address click. 
    var current_shipping_div_id=$('.cart-view-shipping-row-wrapper-selected').attr('id');
    
    $("#"+current_shipping_div_id).trigger('click');






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



    // Adding classes to auth
    $('.web2py_htmltable table').addClass('table-bordered');
    $('.web2py_htmltable table').addClass('manage-view-table');

    $('.w2p_export_menu a').removeClass('btn-default');
    $('.w2p_export_menu a').addClass('btn-primary');

    $(".cart_grid_table_cell:contains(is no longer available)").addClass("cart_item_removed")



    /*Make this conditional for the confirmation page*/
    $("#confirmation input[name=old_password]").val("guestuser");
    $("#confirmation input[name=email").val("");
    $("#confirmation input[name=email]").attr("placeholder", "Enter Email");







}); // End document.ready()
