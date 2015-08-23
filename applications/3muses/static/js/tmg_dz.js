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
// Make sure the dropzone sample still works with the remote db
// Try adding dropzone to datables...


Dropzone.autoDiscover = false;

$(document).ready(function(){

	// Ajax request to wrap around dropzone instantiation so that I can provide the images from the server
	$.ajax({
		type:"POST",

		// right now prepopulate is just getting images associated with product 1
		// eventually it will need to get the id from datatables on click and send that over
		url:'prepopulate_dropzone',

	}).done(function(image_list){

		// Graveyard of different ways to instantiate dropzone
	    // myDropzone=$("div#dropzone_div");
	    // var myDropzone = new Dropzone("#my-awesome-dropzone");
	    // var myDropzone = $("div#dropzone_div").dropzone({ url: "/file/post"});

	    var myDropzone = new Dropzone("div#dropzone_div",{ 

	        url: "/dropzone_upload",

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

					// Creating a file to be added to the dropzone
					var mockFile = { 
						name: image_list[index]['title'], 
						size: 12345, 
						serverId:image_list[index]['id'],
						status: Dropzone.ADDED,
					};

					// Add file to list of uploaded files so that dropzone functions tartgeting all files act appropriately
					myDropzone.files.push(mockFile);

					// I don't really know what this one does
					myDropzone.emit("addedfile", mockFile);

					// Ma-man, ITSolution. Coming up big with createThumbnailFromUrl
					// Without this, I would have had to create my own thumbnail!
					myDropzone.createThumbnailFromUrl(mockFile, image_list[index]['s3_url']);

					// Remove the loading bar
					myDropzone.emit("complete", mockFile);

				}

				// Add db id for image file on upload so that it can be deleted if the user wants that
			    this.on("success", function(file, response) {
			      file.serverId = response; 
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



}); // End document.ready