'use strict';
const reloadInterval = 100;
const reloadEnabled = false;

function errorHandler(error){
    console.log(error);
}

function refreshColor(){
    $.ajax({
        url: '/api/',
        method: 'GET',
        data: {
            "action": "getColor"
        },
        success: (r)=>{
            console.log('Successfully received color.');
            let color = applyBrightness(r.color);
            $('body').css('background-color', `rgb(${color.red}, ${color.green}, ${color.blue})`);
        },
        error: errorHandler
    });
}

function refreshPower(){
	if(reloadEnabled){
		$.ajax({
			url: '/api/',
			method: 'GET',
			data: {
				"action": "getPowerState"
			},
			success: (r)=>{
				console.log('Successfully received power state.');
				if(!r.power){
					$('body').css('background-color', 'black');
				}else{
					refreshColor();
				}
			},
			error: errorHandler
		});
	}
    
}

function applyBrightness(color){
    let ratio = color.brightness/255;
    return {
        red: color.red*ratio,
        green: color.green*ratio,
        blue: color.blue*ratio,
    };
}

$(document).ready(()=>{
	if(reloadEnabled){
		refreshPower();
		setInterval(refreshPower, reloadInterval);
	}
    
});