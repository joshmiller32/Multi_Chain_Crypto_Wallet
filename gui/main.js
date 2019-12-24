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
    //Quit app when closed
    mainWindow.on('closed', function(){
        app.quit();
    })
    
    //Builds the menu from the template below
    const mainMenu = Menu.buildFromTemplate(mainMenuTemplate);
    //Insert menu
    Menu.setApplicationMenu(mainMenu);
});

// Create new window for seed words to display
function createSeedWindow() {
    //create new window
    seedWindow = new BrowserWindow({
        width: 420,
        height: 500,
        title:'Seed Words',
        preload:'./login.js'
    });
    // load html into the window
    seedWindow.loadURL(url.format({
        pathname: path.join(__dirname, 'seedWindow.html'),
        protocol: 'file:',
        slashes: true
    }));
    // remove garbage
    seedWindow.on('close', function(){
        seedWindow = null;
    });
};


const mainMenuTemplate = [
    {
        label:'File',
        submenu:[
            {
                label:'Test',
                click(){
                    createSeedWindow();
                }            
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