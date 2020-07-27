"use strict";
const fs = require('fs');
const child_process = require('child_process');

var socket = require('socket.io-client')('http://2384575c9487.ngrok.io/');
socket.on('connect', function(){
	console.log('connected');
	socket.on('req', function(msg){
		console.log(msg);

		var base64String = 'data:image/png;base64,' + msg.base64;
        var base64Image = base64String.split(';base64,').pop();

        var fileName = 'result.png'
		fs.writeFile(fileName, base64Image, {
            encoding: 'base64'
        }, function(err) {
            console.log('File created: result.png');

			child_process.exec('fcopy.bat result.png', function(error, stdout, stderr) {
				console.log(stdout);
			});
            
        });

	});
});
