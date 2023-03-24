$(document).ready(function() {
    $(".drag-and-drop-container").on("dragover", function(event) {
	event.preventDefault();
	$(this).addClass("dragover");
    });

    $(".drag-and-drop-container").on("dragleave", function(event) {
	event.preventDefault();
	$(this).removeClass("dragover");
    });

    $(".drag-and-drop-container").on("drop", function(event) {
	event.preventDefault();
	$(this).removeClass("dragover");
	$(this).children("input").prop("files", event.originalEvent.dataTransfer.files);
    });
});
