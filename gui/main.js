const electron = require('electron')
const path = require('path')
const url = require('url')

const {app, BrowserWindow, Menu} = electron;

let mainWindow;
let seedWindow;



// Listen for app to be ready
app.on('ready', function(){
    //create the main app window
    mainWindow = new BrowserWindow({width: 800, height: 600});
    // load html into the window
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'loginWindow.html'),
        protocol: 'file:',
        slashes: true
    })); 
    //Quit app when closed
    mainWindow.on('closed', function(){
        app.quit();
    })
    
    //Builds the menu from the template below
    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    //Insert menu
    Menu.setApplicationMenu(mainMenu);
});


const mainMenuTemplate = [
    {
        label:'File',
        submenu:[
            {
                label:'Remove Coins'
            },
            {
                label:'Quit',
                accelerator: process.platform == 'darwin' ? 'Command+Q' :
                'Ctrl+Q',
                click(){
                    app.quit();
                }
            },
            {
                role: 'reload'
            }
        ]
    }
]

// if mac, add empty object to menu to make it render the same as windows
if(process.platform == 'darwin'){
    mainMenuTemplate.unshift({});
}

// add dev tools for debugging
if(process.env.NODE_ENV !== 'production'){
    mainMenuTemplate.push({
        label:'Developer Tools',
        submenu:[
            {
                label:'Toggle DevTools',
                accelerator: process.platform == 'darwin' ? 'Command+I' :
                'Ctrl+I',
                click(item, focusedWindow){
                    focusedWindow.toggleDevTools();
                }
            }
        ]
    })
}