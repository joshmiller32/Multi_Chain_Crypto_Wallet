var word_dict = {}; //We'll have to ask Cam about how to avoid this security vulnerability
let password;
var seed_index;
var coin_purse = {};
var price_dict = {};
var currency;
var xmlDoc;

async function setSeedIndex(index) {
    window.seed_index = index;
    console.log("seed_index:" +seed_index);
}

async function getWords() {
// Create the JAVA containers (variable) and link them to the HTML container.      
// There needs to be a container with the id= to the getElementById() argument.  (HTML Example for the argument used below <div id="word1_box"></div>)
    let word1_container = document.getElementById('word1_box');
    let word2_container = document.getElementById('word2_box');
    let word3_container = document.getElementById('word3_box');
    let word4_container = document.getElementById('word4_box');
    let word5_container = document.getElementById('word5_box');
    let word6_container = document.getElementById('word6_box');
    let word7_container = document.getElementById('word7_box');
    let word8_container = document.getElementById('word8_box');
    let word9_container = document.getElementById('word9_box');
    let word10_container = document.getElementById('word10_box');
    let word11_container = document.getElementById('word11_box');
    let word12_container = document.getElementById('word12_box');  
    
        
// Call into Python and set the JAVA container equal to the Python variable 
// Note the double ()() the first is for arguments intered into the function and the second is for callback function.

// In this case the function returns an object (Python Dict) which we can then access the "key/value" pairs
    
    word_dict = await eel.create_seed()();
    
    word1_container.innerHTML = word_dict.word1;
    word2_container.innerHTML = word_dict.word2;
    word3_container.innerHTML = word_dict.word3;
    word4_container.innerHTML = word_dict.word4;
    word5_container.innerHTML = word_dict.word5;
    word6_container.innerHTML = word_dict.word6;
    word7_container.innerHTML = word_dict.word7;
    word8_container.innerHTML = word_dict.word8;
    word9_container.innerHTML = word_dict.word9;
    word10_container.innerHTML = word_dict.word10;
    word11_container.innerHTML = word_dict.word11;
    word12_container.innerHTML = word_dict.word12;

}


async function getWallet(coin) {
    let QR = document.getElementById('QR');
    let address = document.getElementById('address');
    let balance = document.getElementById('balance');
    let USDbalance = document.getElementById('USDbalance');
    let titleContainer = document.getElementById('title');
    let descrContainer  = document.getElementById('description');
    
    ///getting the variables///
    QRloaded = await eel.make_qr(coin_purse[coin][0].address)();
    var QRcode = new Image;
    
    let acc_balance = await eel.get_balance(coin, coin_purse[coin][0].privkey)();
    console.log(acc_balance);
       
    let usd_balance = acc_balance*price_dict[coin].USD;

    let title = xmlDoc.getElementsByTagName(coin)[0].children[0].innerHTML;
    
    let description = xmlDoc.getElementsByTagName(coin)[0].children[1].innerHTML;
   

    ///populating the wallet section///   
    titleContainer.innerHTML = title;
    descrContainer.innerHTML = description;
    QRcode.onload = function() 
        {
        
        QR.src = this.src;
        }
    QR.src = "images/QR.png";
    address.innerHTML = coin_purse[coin][0].address;
    
    balance.innerHTML = acc_balance;
    USDbalance.innerHTML = usd_balance;
      
}


async function getPrices() {
    let btc_usd_container = document.getElementById('btc_usd');
    let btg_usd_container = document.getElementById('btg_usd');
    let bch_usd_container = document.getElementById('bch_usd');
    let ltc_usd_container = document.getElementById('ltc_usd');
    let dash_usd_container = document.getElementById('dash_usd');
    let doge_usd_container = document.getElementById('doge_usd');
    let xrp_usd_container = document.getElementById('xrp_usd');
    let zec_usd_container = document.getElementById('zec_usd');
    let xlm_usd_container = document.getElementById('xlm_usd');
    
    window.price_dict = await eel.get_prices()();
    btc_usd_container.innerHTML = '$' + price_dict.BTC.USD;
    btg_usd_container.innerHTML = '$' + price_dict.BTG.USD;
    bch_usd_container.innerHTML = '$' + price_dict.BCH.USD;
    ltc_usd_container.innerHTML = '$' + price_dict.LTC.USD;
    dash_usd_container.innerHTML = '$' + price_dict.DASH.USD;
    doge_usd_container.innerHTML = '$' + price_dict.DOGE.USD;
    xrp_usd_container.innerHTML = '$' + price_dict.XRP.USD;
    zec_usd_container.innerHTML = '$' + price_dict.ZEC.USD;
    xlm_usd_container.innerHTML = '$' + price_dict.XLM.USD;
}

async function getBalanceValue() {
    let btc_usd_value = document.getElementById('btc_usd_value');
    let btg_usd_value = document.getElementById('btg_usd_value');
    let bch_usd_value = document.getElementById('bch_usd_value');
    let ltc_usd_value = document.getElementById('ltc_usd_value');
    let dash_usd_value = document.getElementById('dash_usd_value');
    let doge_usd_value = document.getElementById('doge_usd_value');
    let xrp_usd_value = document.getElementById('xrp_usd_value');
    let zec_usd_value = document.getElementById('zec_usd_value');
    let xlm_usd_value = document.getElementById('xlm_usd_value');
    
    let btc_balance = document.getElementById('btc_balance');
    let btg_balance = document.getElementById('btg_balance');
    let bch_balance = document.getElementById('bch_balance');
    let ltc_balance = document.getElementById('ltc_balance');
    let dash_balance = document.getElementById('dash_balance');
    let doge_balance = document.getElementById('doge_balance');
    let xrp_balance = document.getElementById('xrp_balance');
    let zec_balance = document.getElementById('zec_balance');
    let xlm_balance = document.getElementById('xlm_balance');
    
    //price_dict = await eel.get_prices()();
    //console.log(price_dict);
    btc_usd_value.innerHTML = '$' + (Math.round((btc_balance.innerHTML * price_dict.BTC.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    btg_usd_value.innerHTML = '$' + (Math.round((btg_balance.innerHTML * price_dict.BTG.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    bch_usd_value.innerHTML = '$' + (Math.round((bch_balance.innerHTML * price_dict.BCH.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    ltc_usd_value.innerHTML = '$' + (Math.round((ltc_balance.innerHTML * price_dict.LTC.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    dash_usd_value.innerHTML = '$' + (Math.round((dash_balance.innerHTML * price_dict.DASH.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    doge_usd_value.innerHTML = '$' + (Math.round((doge_balance.innerHTML * price_dict.DOGE.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    xrp_usd_value.innerHTML = '$' + (Math.round((xrp_balance.innerHTML * price_dict.XRP.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    zec_usd_value.innerHTML = '$' + (Math.round((zec_balance.innerHTML * price_dict.ZEC.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    xlm_usd_value.innerHTML = '$' + (Math.round((xlm_balance.innerHTML * price_dict.XLM.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
}

async function checkPassword() {
    console.log("Checking Password");
    let input = document.getElementById('loginpassword');
    var pass = input.value;
    let loginCheck = await eel.check_password(pass)();
    console.log("loginCheck");
    console.log(loginCheck);

    if (loginCheck > -1) {
        console.log("launching main window");
        window.seed_index = loginCheck;
        console.log(seed_index);
        return window.location.replace('mainWindow.html?index='+seed_index);

    } else {
        console.log("try again");
        return input.innerHTML = "Incorrect Password";
    }
}

function extractSeed() {
    
    var seed = "";
    for(var key in word_dict) {
      seed += word_dict[key] +  " ";
    }
    return seed;
}
    
    
async function setPassword() {

    let input = document.getElementById('newpassword');
    let pass = input.value;
    let seed = extractSeed();
    console.log(pass);
    console.log(seed);
    let loginCheck = await eel.set_password(pass, seed)();
    window.seed_index = -1
    seed = await eel.decrypt_seed(seed_index)();
    console.log(seed);
    
    return window.location.replace('mainWindow.html?index=-1');
}


async function populateWallet(currency) {

    window.currency = currency
    
    await getPrices();

    //reading xml doc
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                console.log(xmlDoc);
                window.xmlDoc = xmlDoc.responseXML;
            
           }};
        xhttp.open("GET", "text.xml", true);
        xhttp.setRequestHeader("Content-Type", "text/xml");
        xhttp.send();
        window.xmlDoc = xhttp;
        
        //console.log(xmlDoc.documentElement.childNodes)

    console.log(seed_index);
    const seed = await eel.decrypt_seed(seed_index)();
    
    window.coin_purse = await eel.get_wallets(seed)();
    console.log(coin_purse);

    getWallet(currency);
    getBalanceValue();
    
}

async function sendTx(){

    let SendToInput = document.getElementById('sendTo');
    let amountInput = document.getElementById('amount');
    let to = SendToInput.value;
    let amount = amountInput.value;

    tx = await eel.send_tx(currency, coin_purse[currency][0].privkey, to, amount);   
}

function windowClose() {
    window.open('','_parent','');
    window.close();
}

function myFunction(x) {
  //console.log("Row index is: " + x.rowIndex);
}

async function loadXML(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
        // Typical action to be performed when the document is ready:
        //document.getElementById("demo").innerHTML = xhttp.responseText;
        console.log("xml ready");
        console.log(xhttp);
        }
    };
    xhttp.open("GET", "text.xml", true);
    xhttp.setRequestHeader("Content-Type", "text/xml");
    xhttp.send();
    return xhttp.responseXML;
}