console.log('loaded!!!')

images = null

$.ajax({
    url: 'http://localhost:8090/images-json',
    dataType: "json",
    type: "GET",
    async: true,
    data: { },
    success: function (data) {
        images = data
    },
    error: function (xhr, exception) {
        var msg = "";
        if (xhr.status === 0) {
            msg = "Not connect.\n Verify Network." + xhr.responseText;
        } else if (xhr.status == 404) {
            msg = "Requested page not found. [404]" + xhr.responseText;
        } else if (xhr.status == 500) {
            msg = "Internal Server Error [500]." +  xhr.responseText;
        } else if (exception === "parsererror") {
            msg = "Requested JSON parse failed.";
        } else if (exception === "timeout") {
            msg = "Time out error." + xhr.responseText;
        } else if (exception === "abort") {
            msg = "Ajax request aborted.";
        } else {
            msg = "Error:" + xhr.status + " " + xhr.responseText;
        }
    }
});

const redBorderForOneSecond = (elementId) => {
    $(`#${elementId}`).addClass('red-border')
    setTimeout(function() {
        $(`#${elementId}`).removeClass('red-border')
    }, 1000);
}

$('#selected-collection').text('None')

$('#collection').change(() => {
    $('#loaded-images').html('')
    selectedCollection = $('#collection').find('option:selected').text()
    $('#selected-collection').text(selectedCollection)
    $.each(images[selectedCollection], (index, value) => {
        path = value['path']
        image_id = value['image_id']
        const div = $('<div></div>', {
          class: 'image-link-container',
          href: 'images/' + image_id + '/details',
        });
        const a = $('<a></a>', {
          class: 'image-link',
          href: 'images/' + image_id + '/details',
          target: '_blank'
        });
        const img = $('<img />', {
          id: 'image-' + image_id,
          src: 'images/' + image_id,
          alt: 'picture with id ' + image_id
        });
        img.appendTo(a)
        a.appendTo(div)
        div.appendTo($('#loaded-images'))
    });

    if (images[selectedCollection].length === 0) {
        $('#loaded-images').html('Collection has no uploaded images.')
    }
});

$('#add-image-form').submit(() => {
    $("#upload-button").prop('disabled', true);
    return true;
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
    if (repeatPassword !== password) {
        redBorderForOneSecond('password')
        redBorderForOneSecond('repeat-password')
        $('.error').html('Error: Passwords do not match!');
        return false
    }
    $(".error").html('');
    return true
})

$('#change-password-form').submit(() => {
    newPassword = $('#new-password').val()
    repeatNewPassword = $('#repeat-new-password').val()
    if (repeatNewPassword !== newPassword) {
        redBorderForOneSecond('new-password')
        redBorderForOneSecond('repeat-new-password')
        $('.error').html('Error: Passwords do not match!');
        return false
    }
    $('.error').html('');
    return true
})
