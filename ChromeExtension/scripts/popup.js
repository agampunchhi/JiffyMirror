if(window.location.href.indexOf("popup.html") > -1) {
    chrome.storage.local.get([ 'email', 'Authorized' ] , data => {
        if((data.email != null) && (data.Authorized == true)){
            chrome.browserAction.setPopup({popup: "../pages/mirror.html"});
            window.location.replace("../pages/mirror.html");
        };
});
};
if(window.location.href.indexOf("popup.html") > -1){
    setButton = document.getElementById("setEmail");
    setButton.addEventListener("click", function(){
        email = document.getElementById("email").value;
        chrome.storage.local.set({
            'email' : email
        });
        chrome.browserAction.setPopup({popup: "../pages/gdrive.html"});
        setTimeout(function(){}, 2000);
        window.location.assign("../pages/gdrive.html");
    });
}
