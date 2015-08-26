// SO pages used:
// http://stackoverflow.com/questions/24445724/add-existing-image-files-in-dropzone
// http://stackoverflow.com/questions/23369291/dropzone-js-removeallfiles-does-not-remove-mock-files
// http://stackoverflow.com/questions/17400470/dropzone-js-remove-button-with-php/17427379#17427379
// http://stackoverflow.com/questions/29740089/create-thumbnail-for-uploaded-images-on-dropzone-js (ITSolution)

	// Thanks to DanJGer for this way of invoking emit
	// Dropzone.forElement("div#dropzone_div").emit("addedfile", mockFile);

	// Thanks to soneome else for a way of not even invoking emit
	// myDropzone.options.thumbnail.call(myDropzone, mockFile, image_list[index]['s3_url']);


// TODO
// Add filesize to db when uploading a file so that it can be retrieved for dropzone
// Make sure the dropzone sample still works with the remote db (of course it doesn't, because of cross origin stuff)
// Use boto to set content type of freshly uploaded files - super not efficient, but whatever.
// Stupid pyfilesystem doesn't support setting the content type
// Actually, ask this question on stack overflow soon. And maybe the other one I never got an answer to.

// Try adding dropzone to datables...

/*######################################################*/
/* #######       DATATABLES FUNCTIONS         ######### */
/*######################################################*/

/* Formatting function for row details - modify as you need */
function format ( d, columns ) {

    // `d` is the original data object for the row
    // 'columns' is the column information including title, data (name of key in data dictionary), wether its a core value or not, etc.

    // Populate a list of all the fields that are considered core, remember this is being done on a single row!
    // This is vestigal and not necessary anymore. Unless I want to have both additional fields and a subtable. 
    var core_fields=[]

    // Cycle through the columns list (exclude the first one because it is the column for the collapse expand controls)
    for (i=1;i<columns.length;i++) {
    	// if the column is labelled as a core column, that means it should already be in the main table
    	// This is excluding those columns and only showing additional information
    	// For this case, this is basically just the images associated with each product
    	if (columns[i]['core']===true){
    		core_fields.push(columns[i]['data'])
    	}
    }

    // Keeping this around because I may want to use it at some point
     // Begin making the html to show the extra information
     // I still might use this to have both additional info and the images in the coex
	child_rows='<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'
	child_rows+='<tr>'

	 // for each property in the record being clicked
	for (property in d){

		// if the property is not a core field, aka if the property can not be found in the list of core fields
		// (indexOf returns -1 if no match is found)
		if (core_fields.indexOf(property)===-1){

			// for (index in d[property]){

				child_rows+='<tr>'+'<td>'+property+':</td>'+'<td>'+d[property]+'</td>'+'</tr>'
				
					// child_rows+='<td>'
					// child_rows+='<img src='+d[property][index]['s3_url']+'/>'
					// child_rows+=d[property][index]['image_delete_url']
					// child_rows+='</td>'
			// }
		}
	}

	child_rows+='</tr>'
	// complete the table for additional information
	child_rows+='</table>';
	child_rows+='</br>'




	// At the moment, only create a dropzone with the appropriate id based on the id of the product in that row. 
	child_rows+="<div class='dropzone_div dropzone' id='dropzone_div_"+ d['id'] +"'></div>"

    return child_rows

} // Close function format


/* Formatting function for row details - modify as you need */
// This was the format function I used for BATS. I will keep it here for reference. 
function show_remaining_data ( d, columns ) {

    // `d` is the original data object for the row
    // 'columns' is the column information including title, data (name of key in data dictionary), wether its a core value or not, etc.

    // Populate a list of all the fields that are considered core, remember this is being done on a single row!
    var core_fields=[]

    // Cycle through the columns list (exclude the first one because it is the column for the collapse expand controls)
    for (i=1;i<columns.length;i++) {

    	// if the column is labelled as a core column, that means it should already be in the main column tables
    	// This is excluding those columns and only showing additional information
    	if (columns[i]['core']===true){
    		core_fields.push(columns[i]['data'])
    	}
	    	// for (property in columns[i]){
	    	// 	alert(property+' '+columns[i][property]);
	    	// }
    }

    // Begin making the html to show the extra information
	child_rows='<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'

	// for each property in the record being clicked
	for (property in d){
		// alert(property+' '+d[property]);

		// if the property is not a core field, aka if the property can not be found in the list of core fields
		// (indexOf returns -1 if not match is found)
		if (core_fields.indexOf(property)===-1){

			// Then add a row to the additional info table
			child_rows+='<tr>'+'<td>'+property+':</td>'+'<td>'+d[property]+'</td>'+'</tr>'

		}
	}

	// I don't remember what this is doing. 
	if (d.serial_number!==null){
		child_rows
	}

	// complete the table for additional information
	child_rows+='</table>';

    return child_rows
}


/*######################################################*/
/* ########       DROPZONE FUNCTIONS         ########## */
/*######################################################*/

// I have dropzones that I instantiate programmatically, 
// so I don't need dropzone to autodiscover them. 
Dropzone.autoDiscover = false;


$(document).ready(function() {


	// in order to check if we are on the correct page!
    var url_list=window.location.pathname.split('/')
	    // var device_id=url_list[url_list.length-1]
	    // alert(url_list[url_list.length-1]);

	if (url_list[1]==='manage_products_new') {

		var category_name=url_list[2];

		if (category_name==null) {
			dest = '/ajax_manage_products_new/';
		} else {
			dest = '/ajax_manage_products_new/'+category_name;
		};


		table_data=$.ajax({

		    url: dest,
		    dataType: "json",

		}) // end ajax call to set up table

			.done( function ( json ) {

				// alert(json['data']);
				// alert(json['columns'][0]['data']);

			    var table = $('#db_admin').DataTable( {
			        data: json['data'],
			        columns: json['columns'],
			        // scrollX: true,
			        order: [[1, 'asc']],
			        stateSave:true,
			    } );

			    // Add event listener for opening and closing details
			    $('#db_admin').on('click', 'td.details-control', function () {
			        var tr = $(this).closest('tr');
			        var row = table.row( tr );
			 
			        if ( row.child.isShown() ) {
			            // This row is already open - close it
			            row.child.hide();
			            tr.removeClass('shown');
			        }

			        else {
			            // Open this row
			            // This calls format with the row data and the column information
			            // The format function should know what to do with the info not in the table
			            // format just returns html so I'm guessing that row.child exists already and is just being overwritten
			            // with the html returned from format and then displayed. 
			            row.child( format( row.data(), json['columns'] ) ).show();
			            tr.addClass('shown');

			            // But at the moment, all the format function is doing is taking the info and returnting simple html
			            // with a div that has class dropzone and an ID based on the product ID.
			            // Now that that html is present in the DOM, we can programatically instantiate our dropzone.
			            // I want to make this a function at some point. 




						// Ajax request to wrap around dropzone instantiation so that I can provide the images from the server
						// This may be overkill right now, because I already have all the image info from datatables. 
						$.ajax({

							type:"POST",

							// prepopulate dropzone takes a product ID and gets the image information for that product. 
							// Not using a slash in front of the url uses whatever the current last argument is as the url?
							url:'/prepopulate_dropzone/'+row.data()['id'],

						})

							.done(function(image_list){

								// I'm pretty sure I could just make the image list returned by this ajax call the same
								// as the image list available from row.data()['images']

									// Graveyard of different ways to instantiate dropzone
								    // myDropzone=$("div#dropzone_div");
								    // var myDropzone = new Dropzone("#my-awesome-dropzone");
								    // var myDropzone = $("div#dropzone_div").dropzone({ url: "/file/post"});

								// Before we created the dropzone with id dependant on product id, now connect 
								// dropzone to it using the same idea. 
								// There are many ways to initialize a dropzone, but for some reason they
								// make the objects behave differently and have different methods available to them
								// I found that this way makes most of the stack overflow answers work better. 
							    var myDropzone = new Dropzone("div#dropzone_div_"+row.data()['id'],

							    	{

								    	// This is where dropzone will post data when uplodas happen.
								    	// Hopefully it doesn't do anything initially or thats 3 ajax calls already. 
								        url: "/dropzone_upload/"+row.data()['id'],

								        // This adds a link below each image, but the default behavior is to simply remove the preview
								        // the removedfile event is used to actually have the server delete the image. 
								        addRemoveLinks:true,

								        // This effects the prompt so that only images can be selected. 
								        // It also disallows non image files from being dropped.
								        acceptedFiles:'image/*',

								        // And this is some cool stuff I didn't know you could do.
								        // We are in the configuration section of the dropzone initialization 
								        // and we can specifiy all these things to do during it. 
								       	init: function() {

								       		// Just so I don't have to change some of the lines below
								       		var myDropzone = this

								       		// This is from the ajax call. It should be getting all of the images associated with a product
								       		// Again, can I not just use row.data()['images']?
											image_list=jQuery.parseJSON(image_list)

											// Populate the dropzone with the images from the server.
											for (index in image_list){

												// If the image has a file size attribute use that
												// otherwise, use 12345
												if (image_list[index]['filesize']){

													filesize = image_list[index]['filesize'];

												} else {

													filesize = 12345;

												};

												// Create a file to be added to the dropzone
												var mockFile = { 

													name: image_list[index]['title'], 
													serverId:image_list[index]['id'],

													// I haven't been saving filesize all along,
													// so I had that check above . 
													size: filesize, 

													// These were added to try and get thumbnails to work out, it didn't work. 
													// Instead of using thumbnails I'm just resizing the image! Pretty IE
													status: Dropzone.ADDED,
													crossOrigin:'Anonyomous',

												}; // End mockfile init

												// Add file to list of uploaded files so that dropzone functions targeting all files act appropriately
												myDropzone.files.push(mockFile);

												// I don't really know what this one does. Server side images need to behave the same as 
												// ones added by dropzone, though
												myDropzone.emit("addedfile", mockFile);

													// Ma-man, ITSolution. Coming up big with createThumbnailFromUrl
													// Too bad I can't used it because I'm hosting my images 
													// On a different domain. 
													// myDropzone.createThumbnailFromUrl(mockFile, image_list[index]['s3_url']);

												// Tell dropzone where to get the thumbnail, this is actually just the link
												// to the real image file, with css to shrink it down to thumbnail size. 
												myDropzone.emit('thumbnail',mockFile, image_list[index]['s3_url']);

												// Remove the loading bar and any other status stuff. 
												myDropzone.emit("complete", mockFile);

											} // End image loop



											// Javascript is so confusing, so I get that dropzone has these sending, success, and removedFile events
											// But we are inside of a function right now that is called during the init event? I don't know. 


											// send the file size with the form data so I don't have to deal with 
											// python filestorage object to get the filesize. 
											this.on("sending", function(file, xhr, formData) {
											  // Will send the filesize along with the file as POST data.
											  formData.append("filesize", file.size);
											});


											// Add db id for image file on upload so that it can be deleted if the user wants that
										    this.on("success", function(file, response) {
										      file.serverId = response;
											      // file.filesize = file.size;
										    });

										    // When removing an image thumbnail from the dropzone, this function is fired, which politely asks the 
										    // server to delete the file IRL. 
										    this.on("removedfile", function(file) {
										      if (!file.serverId) { return; } // The file hasn't been uploaded
										      $.post("dropzone_delete?id=" + file.serverId); // Send the file id along
										    });



										}, // End init function


						    		}); // End dropzone instantiation

							// There used to be some stuff here, but now its part of the init value in the dropzone declaration

						}); // End Ajax call to get already uploaded images, which I can get from row.data()['images']


			        } // End else clause for when user clicks coex controls and the row is no expanded before click


			    } ); // end on event for collapse controls

			}); // end done section for ajax call to setup table

	} // End check to see if url is manage_products_new
	

} ); // End document ready