console.log('loaded!!!')

$('#selected-collection').text('None')

$("#collection").change(function() {
  $('#selected-collection').text($(this).find('option:selected').text())
});

$('#add-image-form').submit(function() {
    // DO STUFF...
    return true;
});