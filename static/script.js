console.log('loaded!!!')

const redBorderForOneSecond = (elementId) => {
    $(`#${elementId}`).addClass('red-border')
    setTimeout(function() {
        $(`#${elementId}`).removeClass('red-border')
    }, 1000);
}

$('#selected-collection').text('None')

$("#collection").change(() => {
  $('#selected-collection').text($(this).find('option:selected').text())
});

$('#add-image-form').submit(() => {
    // TODO stuff
    return false;
});

$('#add-collection-form').submit(() => {
    $('#collection-name').val($('#collection-name').val().trim())
    collectionName = $('#collection-name').val()
    if (!collectionName) {
        redBorderForOneSecond('collection-name')
        return false
    }
    return true;
});

$('#signup-form').submit(() => {
    password = $('#password').val()
    repeatPassword = $('#repeat-password').val()
    console.log(password, repeatPassword)
    if (repeatPassword !== password) {
        redBorderForOneSecond('password')
        redBorderForOneSecond('repeat-password')
        $(".error").html('Error: Passwords do not match!');
        return false
    }
    $(".error").html('');
    return true
})