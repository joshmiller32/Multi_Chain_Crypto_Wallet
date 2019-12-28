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
    
    let word_dict = await eel.create_seed()();
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