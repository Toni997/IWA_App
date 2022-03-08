console.log('loaded!!!')

$('#selected-collection').text('None')

$("#collection").change(function() {
  $('#selected-collection').text($(this).find('option:selected').text())
});

$('#add-image-form').submit(function() {
    // DO STUFF...
    return true;
});

$('#add-collection-form').submit(function() {
    $('#collection-name').val($('#collection-name').val().trim())
    collectionName = $('#collection-name').val()
    if (!collectionName) {
        $('#collection-name').addClass('red-border')
        setTimeout(function() {
            $('#collection-name').removeClass('red-border')
        }, 1000);
        return false
    }
    return true;
});