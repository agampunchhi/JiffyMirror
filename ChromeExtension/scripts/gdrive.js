if(window.location.href.indexOf("gdrive.html") > -1){
    authBttn = document.getElementById("authLinkOpen");
    existingBttn = document.getElementById("useExisting");
    chrome.storage.local.get('email', function(result) {
        if (result.email != null) {
            chrome.runtime.sendMessage({
                action: "checkExisting",
                email: result.email
            }, function(response) {
                existing = response.Result;
                if(existing == "Found") {
                    authBttn.style.display = "initial"
                    existingBttn.style.display = "initial"
                } else if(existing == "None") {
                    authBttn.style.display = "initial"
                }
            });
        }});
    existingBttn.addEventListener("click", function(){
        chrome.storage.local.set({
            'Authorized': true
        });
        chrome.browserAction.setPopup({popup: "../pages/mirror.html"});
        window.location.assign('../pages/mirror.html');
    });
    authBttn.addEventListener("click", function(){
        chrome.runtime.sendMessage({
            action: "auth"
        });
    });
}
