'use strict';
const darkColorThreshold = 382;
const isNameAutofillEnabled = false;
const tooltipDelay = {
    show: 500,
    hide: 100
};
let deleteButtonPressId = -1;
const periodicRefreshSavedColorsEnabled = false;
function refreshSavedColors(){
    let csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: '/api/',
        method: 'GET',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            action: 'getColors'
        },
        success: function(response){
            let out = $('#saved-colors');
            let numColors = response.colors.length;
            let count = 0;
            out.empty();
            if(response.colors.length <= 1){
                let text = $(document.createElement('span'));
                text.addClass('card-text');
                text.text('No saved colors.');
                out.append(text);
            }else{
                for(let c of response.colors){
                    count++;
                    if(c.name !== 'default'){
                        // create the row
                        let row = $(document.createElement(('div')));
                        if(count < numColors)
                            row.addClass('mb-3');
                        row.addClass('row');

                        // create the column
                        let d = $(document.createElement('div'));
                        d.addClass('col-sm-12');

                        // create the card
                        let card = $(document.createElement('div'));
                        card.addClass('card color-preview');
                        if(count < numColors)
                            row.addClass('mb-3');
                        card.tooltip({
                            delay: tooltipDelay,
                            placement: 'top',
                            title: 'Click to load this color into the above form.'
                        });
                        card.click(function(){
                            let color = $(this).data('color');
                            refreshFormInputs(color);
                            setColorToPreview($('#preview'), color);
                            setColorToPreview($('#preview-old'), color);

                        });

                        // create the card body 1
                        let s = $(document.createElement('div'));
                        s.addClass('card-body align-items-center border-round');


                        // create the hex text
                        let hex = $(document.createElement('span'));
                        hex.addClass('card-text hex-code');
                        hex.text(colorToHexString(c));

                        // create the card's title 1
                        let h = $(document.createElement('strong'));
                        h.addClass('card-text align-items-center');
                        h.text(c.name+' ');

                        // create card body 1 wrapper
                        let link = $(document.createElement('a'));
                        link.attr('href', '#controls');
                        link.addClass('text-link ');

                        // create delete x button
                        let del = $(document.createElement('button'));
                        del.addClass('close');
                        del.attr('type', 'button');
                        del.text('x');
                        del.data('id', c.id);
                        del.click(function(event){
                            event.stopPropagation(); // stop the event from propagating to the parent element
                            deleteButtonPressId = $(this).data('id');
                            bootbox.confirm({
                                title: 'Confirm Deletion',
                                message: 'Are you sure you want to delete this color? Once it\'s deleted, you can\'t get it back.',
                                buttons: {
                                    confirm: {
                                        label: 'Delete',
                                        className: 'btn-danger'
                                    },
                                    cancel: {
                                        label: 'Cancel',
                                        className: 'btn-primary'
                                    }
                                },
                                callback: (result) => {
                                    if(result){
                                        let csrftoken = Cookies.get('csrftoken');
                                        let params = JSON.stringify({
                                            "id": deleteButtonPressId
                                        });
                                        if(deleteButtonPressId){
                                            $.ajax({
                                                url: '/api/',
                                                method: 'POST',
                                                headers: {'X-CSRFToken': csrftoken},
                                                data: {
                                                    "action": "deleteColor",
                                                    "params": params
                                                },
                                                success: (response) => {
                                                    refreshSavedColors();
                                                    changeHidden($('#id'), null);
                                                    /*
                                                    bootbox.alert({
                                                        message: 'Color deleted successfully!',
                                                        buttons: {
                                                            ok: {
                                                                label: 'Ok',
                                                                className: 'btn-primary'
                                                            }
                                                        },
                                                        backdrop: true
                                                    });*/
                                                },
                                                error: handleServerError
                                            });
                                        }
                                    }
                                },
                                closeButton: false // disabling close button since its alignment is off with bootstrap 4+
                            });
                        });
                        del.tooltip({
                            delay: tooltipDelay,
                            placement: 'top',
                            message: 'Delete color'
                        });


                        // add the title and hex to the first column
                        s.append(del);
                        s.append(h);
                        s.append(hex);

                        link.append(s);

                        // add
                        card.append(link);
                        setColorToPreview(card, c);
                        d.append(card);
                        row.append(d);
                        out.append(row);
                    }
                }
            }
        },
        error: handleServerError
    });
}

function applyButtonHandler(){
    let csrftoken = Cookies.get('csrftoken');
    let params = JSON.stringify({
        "red": parseInt($('#red').val()),
        "green": parseInt($('#green').val()),
        "blue": parseInt($('#blue').val()),
        "brightness": parseInt($('#brightness').val()),
    });

    if(validateNumberForms()){
        $.ajax({
            url: '/api/',
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            data: {
                "action": 'setColor',
                "params": params
            },
            success: (response) => {
                //setColorToPreview($('#preview'), response.color);

                //$('#name').val('');
                changeHidden($('#id'), null);
                //disableSpanButton($('#color-delete'));
            },
            error: handleServerError
        });
    }
}

function saveButtonHandler(){
    let csrftoken = Cookies.get('csrftoken');
    let id = $('#id').val();
    let nameElem = $('#name');
    let params = JSON.stringify({
        "name": nameElem.val(),
        "id": parseInt(id),
        "red": parseInt($('#red').val()),
        "green": parseInt($('#green').val()),
        "blue": parseInt($('#blue').val()),
        "brightness": parseInt($('#brightness').val()),
    });
    let nameValidation = validateNameForm();
    let colorValidation = validateNumberForms();
    let isNameUnique = localQueryColors(nameElem.val()) === null;

    // fix to make sure that saving a color without changing its name is allowed
    if(id){
        let currentColor = localQueryColorsId(parseInt(id));
        if(currentColor && currentColor.name === nameElem.val()){
            isNameUnique = true;
        }
    }

    if(nameValidation && colorValidation && isNameUnique){
        if(id){
            bootbox.confirm({
                title: 'Confirm Update',
                message: 'Are you sure you want to update this color?',
                buttons: {
                    confirm: {
                        label: 'Update',
                        className: 'btn-success'
                    },
                    cancel: {
                        label: 'Cancel',
                        className: 'btn-primary'
                    }
                },
                callback: (result) => {
                    if(result){
                        $.ajax({
                            url: '/api/',
                            method: 'POST',
                            headers: {'X-CSRFToken': csrftoken},
                            data: {
                                "action": "updateColor",
                                "params": params
                            },
                            success: (response) => {
                                //setColorToPreview($('#preview'), response.color);
                                refreshSavedColors();
                                changeHidden($('#id'), null);
                                //resetButtonHandler();
                                bootbox.alert({
                                    message: 'Color updated successfully!',
                                    buttons: {
                                        ok: {
                                            label: 'Ok',
                                            className: 'btn-primary'
                                        }
                                    },
                                    backdrop: true
                                });
                            },
                            error: handleServerError
                        });
                    }
                },
                closeButton: false // disabling close button since its alignment is off with bootstrap 4+
            })
        }else {
            $.ajax({
                url: '/api/',
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                data: {
                    "action": "saveColor",
                    "params": params
                },
                success: (response) => {
                    //setColorToPreview($('#preview'), response.color);
                    refreshSavedColors();
                    changeHidden($('#id'), null);
                    //resetButtonHandler();
                    bootbox.alert({
                        message: 'Color created successfully!',
                        buttons: {
                            ok: {
                                label: 'Ok',
                                className: 'btn-primary'
                            }
                        },
                        backdrop: true
                    });
                },
                error: handleServerError
            });
        }
    }

    if(!isNameUnique){
        showPopoverErrorMessage(nameElem, 'This name is already in use. Please enter another.');
    }

}

function refreshFormInputs(color){
    $('#red').val(color.red);
    $('#green').val(color.green);
    $('#blue').val(color.blue);
    $('#brightness').val(color.brightness);

    if(color.name){
        $('#name').val(color.name);
    }

    if(color.id){
        changeHidden($('#id'), color.id);
    }
}

function colorInputChangeHandler(){
    let color = {
        red: parseInt($('#red').val()),
        green: parseInt($('#green').val()),
        blue: parseInt($('#blue').val())
    };
    setColorToPreview($('#preview'), color);
}

function resetButtonHandler(){
    changeHidden($('#id'), null);
}

function powerButtonHandler(){
    let csrftoken = Cookies.get('csrftoken');
    $.ajax({
        url: '/api/',
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        data: {
            "action": "togglePwrState"
        },
        success: (r) => {
            $('#power-toggle').prop('checked', r.power);
        },
        error: handleServerError
    });
}

function refreshPowerToggleButton(){
    $.ajax({
        url: '/api/',
        method: 'GET',
        data: {
            "action": 'getPowerState'
        },
        success: (r) => {
            $('#power-toggle').prop('checked', r.power);
        },
        error: handleServerError
    });
}

function deleteButtonPressHandler(){
    bootbox.confirm({
        title: 'Confirm Deletion',
        message: 'Are you sure you want to delete this color? Once it\'s deleted, you can\'t get it back.',
        buttons: {
            confirm: {
                label: 'Delete',
                className: 'btn-danger'
            },
            cancel: {
                label: 'Cancel',
                className: 'btn-primary'
            }
        },
        callback: (result) => {
            if(result){
                let csrftoken = Cookies.get('csrftoken');
                let id = $('#id').val();
                let params = JSON.stringify({
                    "id": id
                });
                if(id){
                    $.ajax({
                        url: '/api/',
                        method: 'POST',
                        headers: {'X-CSRFToken': csrftoken},
                        data: {
                            "action": "deleteColor",
                            "params": params
                        },
                        success: (response) => {
                            refreshSavedColors();
                            changeHidden($('#id'), null);
                            bootbox.alert({
                                message: 'Color deleted successfully!',
                                buttons: {
                                    ok: {
                                        label: 'Ok',
                                        className: 'btn-primary'
                                    }
                                },
                                backdrop: true
                            });
                        },
                        error: handleServerError
                    });
                }
            }
        },
        closeButton: false // disabling close button since its alignment is off with bootstrap 4+
    });
}

function colorToHexString(color){
    let r = ('00' + parseInt(color.red).toString(16).toUpperCase()).slice(-2);
    let g = ('00' + parseInt(color.green).toString(16).toUpperCase()).slice(-2);
    let b = ('00' + parseInt(color.blue).toString(16).toUpperCase()).slice(-2);
    return `#${r}${g}${b}`;
}

function isColorDark(color){
    return (color.red + color.green + color.blue) <= darkColorThreshold;
}

function validateNameForm(){
    let name = $('#name').val();
    let container = $('#name-row');
    //container.find('.alert').alert('close');
    if(!name || name === ''){
        showPopoverErrorMessage($('#name'), 'Please enter a name.');
        //warningAlert(container,'Please enter a name.');
        return false;
    }else if(name === 'default'){
        showPopoverErrorMessage($('#name'),
            'The name \'default\' is reserved. Please enter a different name.');
        //warningAlert(container, 'The name \'default\' is reserved. Please enter a different name.')
        return false;
    }
    return true;
}

function isValueInRange(value){
    return value >= 0 && value <= 255;
}

function validateRedForm(){
    let red = $('#red').val();
    let container = $('#red-row');
    container.find('.alert').alert('close');
    if(!red){
        showPopoverErrorMessage($('#red'), 'Please enter a red value.');
        //warningAlert(container, 'Please enter a red value.');
        return false
    }else if(!isValueInRange(red)){
        showPopoverErrorMessage($('#red'), 'Please enter a red value between 0 and 255.');
        //warningAlert(container, 'Please enter a red value between 0 and 255.');
        return false
    }
    return true;
}

function validateGreenForm(){
    let val = $('#green').val();
    let container = $('#green-row');
    container.find('.alert').alert('close');
    if(!val){
        showPopoverErrorMessage($('#green'), 'Please enter a green value.');
        //warningAlert(container, 'Please enter a green value.');
        return false
    }else if(!isValueInRange(val)){
        showPopoverErrorMessage($('#green'), 'Please enter a green value between 0 and 255.');
        //warningAlert(container, 'Please enter a green value between 0 and 255.');
        return false
    }
    return true;
}

function validateBlueForm(){
    let val = $('#blue').val();
    let container = $('#blue-row');
    container.find('.alert').alert('close');
    if(!val){
        showPopoverErrorMessage($('#blue'), 'Please enter a blue value.');
        //warningAlert(container, 'Please enter a blue value.');
        return false
    }else if(!isValueInRange(val)){
        showPopoverErrorMessage($('#blue'), 'Please enter a blue value between 0 and 255.');
        //warningAlert(container, 'Please enter a blue value between 0 and 255.');
        return false
    }
    return true;
}

function validateBrightnessForm(){
    let val = $('#brightness').val();
    let container = $('#brightness-row');
    container.find('.alert').alert('close');
    if(!val){
        showPopoverErrorMessage($('#brightness'), 'Please enter a brightness value.');
        //warningAlert(container, 'Please enter a brightness value.');
        return false
    }else if(!isValueInRange(val)){
        showPopoverErrorMessage($('#brightness'), 'Please enter a brightness value between 0 and 255.');
        //warningAlert(container, 'Please enter a brightness value between 0 and 255.');
        return false
    }
    return true;
}

function validateNumberForms(){
    let r = validateRedForm();
    let g = validateGreenForm();
    let b = validateBlueForm();
    let br = validateBrightnessForm();
    return r && g && b && br;
}

function handleServerError(error){
    let alerts = $('#alerts');

    // close any pending alerts.
    alerts.find('.alert').alert('close');

    let div = $(document.createElement('div'));
    let button = $(document.createElement('button'));
    let span = $(document.createElement('span'));

    // set up the div
    div.addClass('alert alert-danger alert-dismissible fade show');
    div.attr('role', 'alert');
    let strong = $(document.createElement('strong'));
    strong.text('Server Responded With Error: ');
    let message = $(document.createElement('span'));
    if(error.responseJSON && error.responseJSON.message)
        message.text(error.responseJSON.message);
    else
        message.text(error.responseText);
    div.append(strong);
    div.append(message);

    // set up the button
    button.addClass('close');
    button.attr('type','button');
    button.attr('aria-label', 'Close');
    button.attr('data-dismiss', 'alert');

    // set up the span
    span.attr('aria-hidden', true);
    span.text('x');

    // add the span to the button
    button.append(span);

    // add the button to the div
    div.append(button);

    // add the alert to the alerts container
    alerts.append(div);

}

function disableSpanButton(span){
    span.css('pointer-events', 'none');
    span.attr('aria-disabled', true);
    span.addClass('disabled');
}

function enableSpanButton(span){
    span.css('pointer-events', 'auto');
    span.attr('aria-disabled', false);
    span.removeClass('disabled');
}

function localQueryColors(name){
    let colors = $('.color-preview');
    let found = null;
    for(let c of colors){
        let n = $(c).data('color').name;
        if(n === name) {
            found = $(c).data('color');
            break;
        }
    }

    return found;
}

function localQueryColorsNumeric(color){
    let colors = $('.color-preview');
    let found = null;
    for(let c of colors){
        let clr = $(c).data('color');
        if(
            clr.red === color.red &&
            clr.green === color.green &&
            clr.blue === color.blue
        ) {
            found = clr;
            break;
        }
    }

    return found;
}

function localQueryColorsId(id){
    let colors = $('.color-preview');
    let found = null;
    for(let c of colors){
        let n = $(c).data('color').id;
        if(n === id) {
            found = $(c).data('color');
            break;
        }
    }

    return found;
}

function setColorToPreview(obj, color){

    // store the color in the card body
    obj.data('color', color);

    // update bg color
    obj.css('background-color', `rgb(${color.red}, ${color.green}, ${color.blue})`);

    // set text color of the card
    if(isColorDark(color)){
        obj.removeClass('text-dark');
        obj.addClass('text-light');
    }else{
        obj.removeClass('text-light');
        obj.addClass('text-dark');
    }

    // refresh hex value
    obj.find('.hex-code').text(colorToHexString(color));

}

function nameOnChange(){
    if(isNameAutofillEnabled){
        let name = $(this).val();
        let result = localQueryColors(name);
        if(result !== null){
            changeHidden($('#id'), result.id);
        }
    }
}

// popover error message functions
function popoverErrorContentCallback(){
    return $(this).data('error');
}

function showPopoverErrorMessage(obj, message){
    obj.data('error', message);
    obj.popover('show');
}

function hidePopoverErrorMessage(obj){
    obj.popover('hide');
    obj.data('error', '');
}

function hidePopoverErrorMessage_this(event){
    hidePopoverErrorMessage($(this));
}

function saveAsButtonHandler(event){
    let csrftoken = Cookies.get('csrftoken');
    let nameValidation = validateNameForm();
    let colorValidation = validateNumberForms();
    let nameElem = $('#name');
    let isNameUnique = localQueryColors(nameElem.val()) === null;
    let params = JSON.stringify({
        "name": nameElem.val(),
        "red": parseInt($('#red').val()),
        "green": parseInt($('#green').val()),
        "blue": parseInt($('#blue').val()),
        "brightness": parseInt($('#brightness').val()),
    });

    if(nameValidation && colorValidation && isNameUnique){
        $.ajax({
            url: '/api/',
            method: 'POST',
            headers: {'X-CSRFToken': csrftoken},
            data: {
                "action": "saveColor",
                "params": params
            },
            success: (response) => {
                refreshSavedColors();
                changeHidden($('#id'), null);
                bootbox.alert({
                    message: 'Color created successfully!',
                    buttons: {
                        ok: {
                            label: 'Ok',
                            className: 'btn-primary'
                        }
                    },
                    backdrop: true
                });
            },
            error: handleServerError
        });
    }

    if(!isNameUnique){
        showPopoverErrorMessage(nameElem, 'This name is already in use. Please enter another.');
    }
}

function changeHidden(obj, value){
    obj.val(value).trigger('change');
}

function idOnChange(){
    let id = parseInt($(this).val());
    if(id){
        // enable the delete button
        enableSpanButton($('#color-delete'));

        // retrieve the color to load
        let color = localQueryColorsId(id);

        // fill the loaded color into the input fields
        $('#name').val(color.name);
        $('#red').val(color.red);
        $('#green').val(color.green);
        $('#blue').val(color.blue);
        $('#brightness').val(color.brightness);

        // update the previews
        setColorToPreview($('#preview'), color);
        setColorToPreview($('#preview-old'), color);

    }else{
        // the value was unset
        $.ajax({
            url: '/api/',
            method: 'GET',
            data: {
                action: 'getColor'
            },
            success: (response) => {
                // disable the delete button
                disableSpanButton($('#color-delete'));

                // fill the retrieved color into the form inputs
                $('#name').val('');
                $('#red').val(response.color.red);
                $('#green').val(response.color.green);
                $('#blue').val(response.color.blue);
                $('#brightness').val(response.color.brightness);

                // update the previews
                setColorToPreview($('#preview'), response.color);
                setColorToPreview($('#preview-old'), response.color);
            }
        });
    }
}

function searchOnChange(event){
    let result = localQueryColors($(this).val());
    let search = $('#preview-search');
    if(result !== null){
        searchPreview_setColorToPreview(result);
        search.data('id', result.id);
    }else{
        searchPreview_setColorToPreview({red: 0, green: 0, blue: 0});
        $('#preview-search').css('background-color', 'var(--gray)');
        $('#preview-search').css('color', 'var(--light)');
        search.find('.hex-code').text('#------');
        search.data('id', null);
    }
}

function searchPreview_setColorToPreview(color){
    // do normal preview update
    setColorToPreview($('#preview-search'), color);

    // update internal id value to be used by the onclick handler for the button
}

function searchPreview_onClick(event){
    let id = $(this).data('id');
    if(id){
        $('#search').val('').trigger('change');
        changeHidden($('#id'), id);
    }

}

$(document).ready(()=>{
    // register event listeners for the form buttons
    $('#color-set').click(applyButtonHandler);
    $('#color-save').click(saveButtonHandler);
    $('#color-reset').click(resetButtonHandler);
    $('#power-toggle').click(powerButtonHandler);
    $('#color-save-as').click(saveAsButtonHandler);
    $('#preview-search').click(searchPreview_onClick);

    // disable the delete button
    let delButton = $('#color-delete');
    delButton.click(deleteButtonPressHandler);
    disableSpanButton(delButton);

    // register event listeners
    $('input[type=number]').on({
        change: colorInputChangeHandler,
        keyup: colorInputChangeHandler,
        focus: colorInputChangeHandler
    });
    $('#search').on({
        change: searchOnChange,
        keyup: searchOnChange,
        focus: searchOnChange
    });

    $('#id').change(idOnChange);
    $('#name').keyup(nameOnChange);


    // setup popovers
    $('#name').popover({
        content: popoverErrorContentCallback,
        trigger: 'manual'
    });

    $('#red').popover({
        content: popoverErrorContentCallback,
        trigger: 'manual'
    });

    $('#green').popover({
        content: popoverErrorContentCallback,
        trigger: 'manual'
    });

    $('#blue').popover({
        content: popoverErrorContentCallback,
        trigger: 'manual'
    });

    $('#brightness').popover({
        content: popoverErrorContentCallback,
        trigger: 'manual'
    });

    // event listeners to clear popovers
    $('#name').click(hidePopoverErrorMessage_this);
    $('#red').click(hidePopoverErrorMessage_this);
    $('#green').click(hidePopoverErrorMessage_this);
    $('#blue').click(hidePopoverErrorMessage_this);
    $('#brightness').click(hidePopoverErrorMessage_this);

    // refresh the list of colors and the power toggle button every minute
	// (if enabled)
	if(periodicRefreshSavedColorsEnabled){
		setInterval(function(){
			refreshSavedColors();
			refreshPowerToggleButton();
		}, 60000);
	}
    

    // request the current color and refresh inputs/previews with the result
    $.ajax({
        url: '/api/',
        method: 'GET',
        data: {
            "action": 'getColor'
        },
        success: (r) => {
            refreshFormInputs(r.color);
            setColorToPreview($('#preview'), r.color);
            setColorToPreview($('#preview-old'), r.color);
        },
        error: handleServerError
    });

    $('#saved-colors-header').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Click to expand/collapse.'});

    $('#name').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Name that will be used to identify the color when saved.'
    });

    $('#red').tooltip({
        delay: tooltipDelay,
        placement: 'right',
        title: 'Value between 0 and 255. Red component of RGB color.'
    });

    $('#green').tooltip({
        delay: tooltipDelay,
        placement: 'right',
        title: 'Value between 0 and 255. Green component of RGB color.'
    });

    $('#blue').tooltip({
        delay: tooltipDelay,
        placement: 'right',
        title: 'Value between 0 and 255. Blue component of RGB color.'
    });

    $('#brightness').tooltip({
        delay: tooltipDelay,
        placement: 'right',
        title: 'Value between 0 and 255. Controls brightness of the LED strip.'
    });

    $('#color-set').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Set the above color to the LED strip.'
    });

    $('#color-save').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Save or update the above color in the database.'
    });

    $('#color-reset').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Reset the above forms to the current color of the LED strip.'
    });

    $('.switch').tooltip({
        delay: tooltipDelay,
        placement: 'bottom',
        title: 'Turn the LED strip on or off.'
    });

    $('#color-save-as').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Save a copy of the above color in the database.'
    });

    $('#color-delete').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Remove the loaded color from the database.'
    });

    $('#preview').tooltip({
        delay: tooltipDelay,
        placement: 'left',
        title: 'Preview of the color in the form.'
    });

    $('#preview-old').tooltip({
        delay: tooltipDelay,
        placement: 'right',
        title: 'Preview of the previous color for comparison.'
    });

    $('#search').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Enter the name of a saved color here to load it into the button.'
    });

    $('#preview-search').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Changes based on name in the search form. Click to load the saved color into the below form.'
    });

    $('#led-link').click(()=>{
        window.open('/strip/', 'popup', 'width=500,height=500');
        return false;
    });

    $('#led-link').tooltip({
        delay: tooltipDelay,
        placement: 'top',
        title: 'Opens the emulated LED strip in a 500x500 popup window.'
    });

    refreshSavedColors();
    refreshPowerToggleButton();



});