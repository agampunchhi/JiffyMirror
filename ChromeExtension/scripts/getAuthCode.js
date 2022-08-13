setTimeout(function(){
    if (document.getElementsByClassName('fD1Pid') != null) {
    authCode = document.getElementsByClassName('fD1Pid')[0].innerHTML;
    chrome.storage.local.get('email', function(result) {
        if (result.email != null) {
            chrome.runtime.sendMessage({
                action: "getAuthCode",
                email: result.email,
                authCode: authCode
            }, function(response) {
                console.log(response);
                if (response.action == "authSuccess") {
                    chrome.storage.local.set({
                        'Authorized': true
                    });
                    addMessage();
                }
            });
        }
    });
    return;
    }
}, 1000);



function addMessage() {
    var message = document.createElement('div');
    message.className = "message";
    message.innerHTML = "Success. Close this tab and open PellMirror extension";
    message.style.fontSize = "20px";
    message.style.fontWeight = "bold";
    message.style.border = "5px solid green";
    message.style.borderRadius = "20px";
    message.style.padding = "10px";
    message.style.margin = "10px";
    message.style.backgroundColor = "#C7FFA1";
    document.getElementsByClassName('DRS7Fe bxPAYd k6Zj8d')[0].parentNode.insertBefore(message, document.getElementsByClassName('DRS7Fe bxPAYd k6Zj8d')[0].nextSibling);
}
