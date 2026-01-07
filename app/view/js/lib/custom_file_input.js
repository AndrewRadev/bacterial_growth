$.fn.customFileInput = function(options) {
  let $container = $(this);

  let $fileInput = options.$input || $container.find('input[type=file]');
  if ($fileInput.length == 0) {
    console.error("No real file input found, either as an option, or inside the container");
    return;
  }

  $container.on('dragover', '.js-file-upload', function(e) {
    e.preventDefault();
    $(this).addClass('drop-hover');
  });

  $container.on('dragleave', '.js-file-upload', function(e) {
    e.preventDefault();
    $(this).removeClass('drop-hover');
  });

  $container.on('drop', '.js-file-upload', function(e) {
    e.preventDefault();

    $fileInput[0].files = e.originalEvent.dataTransfer.files;

    $(this).removeClass('drop-hover');
    $fileInput.trigger('change');
  });
}
