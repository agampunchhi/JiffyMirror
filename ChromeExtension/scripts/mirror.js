if(window.location.href.indexOf('mirror.html') > -1) {
    chrome.storage.local.get([ 'email', 'Authorized' ] , data => {
        if((data.email == null) && (data.Authorized == false)){
            chrome.browserAction.setPopup({popup: "../popup.html"});
            window.location.replace("../popup.html");
        };
    });
}

if(window.location.href.indexOf('mirror.html') > -1) {
    sendBttn = document.getElementById('sendLink');
    sendBttn.addEventListener('click', function() {
        mirrorLink = document.getElementById('link').value;
        folderLink = document.getElementById('folderID').value;
        chrome.storage.local.get('folderArray', data => {
            if(data.folderArray == null) {
                chrome.storage.local.set({'folderArray': [folderLink]}, () => {});
            } else {
                if(data.folderArray.indexOf(folderLink) == -1) {
                    if(folderLink != "") {
                        data.folderArray.push(folderLink);
                        chrome.storage.local.set({'folderArray': data.folderArray}, () => {});
                    }
                }}});
        if(folderLink == "") {
            folderLink = "root";
            folderID = ""
        } else {
            folderID = folderLink
        }
        chrome.storage.local.set({'folderLink': folderID})
        if(mirrorLink.indexOf('http') != -1 || mirrorLink.indexOf('https') != -1 || mirrorLink.indexOf('magnet') != -1) {
            chrome.storage.local.get('email', function(data) {
            chrome.runtime.sendMessage({
                action: "mirrorHTTP",
                link: mirrorLink,
                email: data.email,
                folder: folderLink
            }, function(response) {
                dwnLoadBttn = document.getElementById('sendLink');
                dwnLoadBttn.style.marginTop = "0px";
                if(response.action == 'Added') {
                    showResponse('Added. Check Status', '#C6FFC6', '#6AFF6A');
                    setTimeout(function() {
                        document.getElementById('response').remove();
                    }, 3000);
                } else {
                    showResponse("Some error occured", '#FFD6D6', '#FF6A6A');
                    setTimeout(function() {
                        document.getElementById('response').remove();
                    }, 3000);
                    console.log(response.action);
                }
            });
        });
        }
    });
}

function showResponse(title, bgColor, color) {
    if(document.getElementById('response')) {
        document.getElementById('response').remove();
    }
    var message = document.createElement('div');
    message.style.width = "auto";
    message.className = "message";
    message.id = "response";
    message.innerHTML = title;
    message.style.fontSize = "10px";
    message.style.fontWeight = "bold";
    message.style.border = "3px solid "+color;
    message.style.borderRadius = "20px";
    message.style.padding = "5px";
    message.style.margin = "7px";
    message.style.backgroundColor = bgColor;
    document.getElementById('sendLink').parentNode.insertBefore(message, document.getElementById('sendLink').nextSibling);
}

if(window.location.href.indexOf('mirror.html') > -1) {
    chrome.storage.local.get(['email', 'folderLink'], function(data) {
        if(data.email != null) {
            if(data.folderLink != null){
            document.getElementById('folderID').value = data.folderLink
            } else {
                document.getElementById('folderID').value = ""
            }
            showBttn = document.getElementById('emailShow');
            showBttn.addEventListener('mouseover', function() {
                showBttn.innerText = data.email;
            });
            showBttn.addEventListener('mouseleave', function() {
                showBttn.innerText = 'LOGOUT';
            });
            showBttn.addEventListener('click', function() {
                chrome.storage.local.set({'email': null, 'Authorized': false}, function() {
                    window.location.replace("../popup.html");
                    chrome.browserAction.setPopup({popup: "../popup.html"});
                });
            });
        }
    });
}

if(window.location.href.indexOf('mirror.html') > -1) {
    statusBttn = document.getElementById('statusBttn');
    statusBttn.addEventListener('click', function() {
        window.location.replace("../pages/status.html");
    });
}
