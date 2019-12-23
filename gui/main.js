const electron = require('electron');
const url = require('url');
const path = require('path');

const {app, BrowserWindow, Menu} = electron;

let mainWindow;
let seedWindow;

// Listen for app to be ready
app.on('ready', function(){
    //create new window
    mainWindow = new BrowserWindow({});
    // load html into the window
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'loginWindow.html'),
        protocol: 'file:',
        slashes: true
    }));  
    
    //Builds the menu from the template below
    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    //Insert menu
    Menu.setApplicationMenu(mainMenu);
});


function createSeedWindow() {
    //create new window
    seedWindow = new BrowserWindow({
        width: 200,
        height: 500,
        title:'Seed Words'
    });
    // load html into the window
    seedWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'seedWindow.html'),
        protocol: 'file:',
        slashes: true
    }));  
};


const mainMenuTemplate = [
    {
        label:'File',
        submenu:[
            {
                label:'Add Coins'
            },
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
            }
        ]
    }
]
