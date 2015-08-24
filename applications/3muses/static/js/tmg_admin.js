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
// Make sure the dropzone sample still works with the remote db (of course it doesn't)
// Use boto to set content type of freshly uploaded files - super not efficient, but whatever.
// Stupid pyfilesystem doesn't support setting the content type
// Actually, ask this question on stack overflow soon. And maybe the other one I never got an answer to. 
// Try adding dropzone to datables...



/* Formatting function for row details - modify as you need */
function format ( d, columns ) {

    // `d` is the original data object for the row
    // 'columns' is the column information including title, data (name of key in data dictionary), wether its a core value or not, etc.

    // Populate a list of all the fields that are considered core, remember this is being done on a single row!
    // This is vestingal and not necessary anymore.
    var core_fields=[]

    // Cycle through the columns list (exclude the first one because it is the column for the collapse expand controls)
    for (i=1;i<columns.length;i++) {
    	// if the column is labelled as a core column, that means it should already be in the main column tables
    	// This is excluding those columns and only showing additional information
    	// For this case, this is basically just the images associated with each product
    	if (columns[i]['core']===true){
    		core_fields.push(columns[i]['data'])
    	}
    }

    // Begin making the html to show the extra information
	// child_rows='<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'
	// child_rows+='<tr>'

	// for each property in the record being clicked
	// for (property in d){

	// 	// if the property is not a core field, aka if the property can not be found in the list of core fields
	// 	// (indexOf returns -1 if not match is found)
	// 	if (core_fields.indexOf(property)===-1){

	// 		for (index in d[property]){
	// 			child_rows+='<td>'
	// 			child_rows+='<img src='+d[property][index]['s3_url']+'/>'
	// 			child_rows+=d[property][index]['image_delete_url']
	// 			child_rows+='</td>'
	// 		}
			
	// 	}
	// }

	// child_rows+='</tr>'

	// // complete the table for additional information
	// child_rows+='</table>';

	// child_rows+='</br>'



	child_rows="<div class='dropzone_div dropzone' id='dropzone_div_"+ d['id'] +"'></div>"

    return child_rows
}


/* Formatting function for row details - modify as you need */
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

	if (d.serial_number!==null){
		child_rows
	}

	// complete the table for additional information
	child_rows+='</table>';

    return child_rows
}




Dropzone.autoDiscover = false;


$(document).ready(function() {



	// $("#db_admin").DataTable();




	// in order to check if we are on the correct page!
    var url_list=window.location.pathname.split('/')
	    // var device_id=url_list[url_list.length-1]
	    // alert(url_list[url_list.length-1]);



  //   if (url_list[1]==='device') {

  //   	// Get the device ID from the url
		// var device_id=url_list[2]


		// // ###################################
		// // For viewing the data with datatables
		// // ###################################

		// $.ajax({
		//     url: '/ajax_get_device_field_names/'+device_id,
		//     dataType: "json",
		// })
		// 	.done( function ( json ) {

		//         var table = $('#aws-data-table').dataTable( {
		// 			processing: true,
		// 		    serverSide: true,
		// 		    scrollY: 300,
	 //                stateSave:true,
	 //                // order:[[1,'desc']],
	 //                scrollCollapse:false,
		// 		 	ajax:'/ajax_view_aws_timeseries/'+device_id,
		// 			columns:json
		// 		});

		//     }); // end datatables for device page





// There will be an ajax function that takes the table name and returns
// The core columns names for the table
// The data for the table
// table settings?

// The ajax function that will do this is called
// ajax_aws_table/tablename

// it takes an argument which is the tablename in aws

// The argument comes from the url, which will be called
// aws_table/tablename



	// ###############################################
	// General Code for Viewing AWS data in datatables
	// ###############################################

	// if (url_list[1]==='manage_products_new') {

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
			        scrollX: true,
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
			            row.child( format( row.data(), json['columns'] ) ).show();
			            tr.addClass('shown');

















	// Ajax request to wrap around dropzone instantiation so that I can provide the images from the server
	$.ajax({
		type:"POST",

		// right now prepopulate is just getting images associated with product 1
		// eventually it will need to get the id from datatables on click and send that over
		url:'prepopulate_dropzone/'+row.data()['id'],

	}).done(function(image_list){

		// Graveyard of different ways to instantiate dropzone
	    // myDropzone=$("div#dropzone_div");
	    // var myDropzone = new Dropzone("#my-awesome-dropzone");
	    // var myDropzone = $("div#dropzone_div").dropzone({ url: "/file/post"});

	    var myDropzone = new Dropzone("div#dropzone_div_"+row.data()['id'],{ 

	        url: "/dropzone_upload/"+row.data()['id'],

	        // This adds a link below each image, but the default behavior is to simply remove the preview
	        // the removedfile event is used to actually have the server delete the image. 
	        addRemoveLinks:true,

	        acceptedFiles:'image/*',

	       	init: function() {

	       		// Just so I don't have to change some of the lines below
	       		var myDropzone = this

	       		// This is from the ajax call. It should be getting all of the images associated with a product
				image_list=jQuery.parseJSON(image_list)

				// Populate the dropzone with the images from the server.
				// I'm having trouble creating the thumbnails right now.
				for (index in image_list){


					if (image_list[index]['filesize']){
						filesize = image_list[index]['filesize'];
					} else {
						filesize = 12345;
					};

					// Creating a file to be added to the dropzone
					var mockFile = { 
						name: image_list[index]['title'], 
						size: filesize, 
						serverId:image_list[index]['id'],
						status: Dropzone.ADDED,
						crossOrigin:'Anonyomous',
					};

					// Add file to list of uploaded files so that dropzone functions tartgeting all files act appropriately
					myDropzone.files.push(mockFile);

					// I don't really know what this one does
					myDropzone.emit("addedfile", mockFile);

					// Ma-man, ITSolution. Coming up big with createThumbnailFromUrl
					// Without this, I would have had to create my own thumbnail!
					// myDropzone.createThumbnailFromUrl(mockFile, image_list[index]['s3_url']);
					myDropzone.emit('thumbnail',mockFile, image_list[index]['s3_url']);

					// Remove the loading bar
					myDropzone.emit("complete", mockFile);

				}


				// send the file size with the form data so I don't have to deal with python filestorage object to get the filesize. 
				this.on("sending", function(file, xhr, formData) {
				  // Will send the filesize along with the file as POST data.
				  formData.append("filesize", file.size);
				});


				// Add db id for image file on upload so that it can be deleted if the user wants that
			    this.on("success", function(file, response) {
			      file.serverId = response;
			      // alert(file.size);
			      file.filesize = file.size;
			    });

			    // When removing an image thumbnail from the dropzone, this function is fired, which politely asks the 
			    // server to delete the file. 
			    this.on("removedfile", function(file) {
			      if (!file.serverId) { return; } // The file hasn't been uploaded
			      $.post("dropzone_delete?id=" + file.serverId); // Send the file id along
			    });
			  },

	    }); // End dropzone instantiation

		// There used to be some stuff here, but now its part of the init value in the dropzone declaration

	}); // End Ajax call to get already uploaded images





















			        }





































			    } ); // end on event for collapse controls

			}); // end done section for ajax call to setup table




 
	// }; // end if clause for checking if page name is aws_table






} ); // End document ready