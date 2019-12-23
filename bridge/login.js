function new_user() {
    var python = require("python-shell")
    var path = require("path")
    
    var password = document.getElementById("password").value
    document.getElementById("password").value = "";
    
    var options = {
        scriptPath: path.join(__dirname, '../backend/'),
    }
    
    var seed = new python('wallet.py', options);
    
    seed.on('message', function(message) {
        swal(message);
    })
    
};
