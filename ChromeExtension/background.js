chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action == "auth") {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "https://putamirrorservice.loca.lt/api/getAuthLink", true);
        xhr.setRequestHeader("Bypass-Tunnel-Reminder", "true");
        xhr.onreadystatechange = function()
        {
            if(xhr.readyState == XMLHttpRequest.DONE)
            {
                response = xhr.responseText;
                authLink = JSON.parse(response);
                console.log(response);
                chrome.tabs.create({url: authLink});
                chrome.chromeAction.setPopup({popup: "../pages/mirror.html"});
            }
        }
        xhr.send();
        return true;
    }
    if (request.action == "getAuthCode") {
        email = request.email;
        authCode = request.authCode;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "https://putamirrorservice.loca.lt/api/recieveAuthLink?code="+authCode+"&email="+email, true);
        xhr.setRequestHeader("Bypass-Tunnel-Reminder", "true");
        xhr.onreadystatechange = function()
        {
            if(xhr.readyState == XMLHttpRequest.DONE)
            {
                response = xhr.responseText;
                console.log(response);
                if(response == 'Success')
                {
                    sendResponse({action: "authSuccess"});
                    chrome.chromeAction.setPopup({popup: "../pages/mirror.html"});
                    window.location.assign('../pages/mirror.html');
                }
            }
        }
        xhr.send();
        return true;
    }
    if(request.action == "mirrorHTTP") {
        dwnURL = request.link;
        emailAddress = request.email;
        folderID = request.folder;
        var xhr = new XMLHttpRequest();
        reqLink = "https://putamirrorservice.loca.lt/api/download?email=" + emailAddress + "&link="+ dwnURL + "&folderID=" + folderID;
        xhr.open("GET", "https://putamirrorservice.loca.lt/api/download?email=" + emailAddress + "&link="+ dwnURL + "&folderID=" + folderID, true);
        xhr.setRequestHeader("Bypass-Tunnel-Reminder", "true");
        xhr.onreadystatechange = function()
        {
            if(xhr.readyState == XMLHttpRequest.DONE)
            {
                response = xhr.responseText;
                console.log(response);
                sendResponse({action: this.response});
            }
        }
        xhr.send();
        return true;
    }
    
    if(request.action == "statusFetch") {
        email = request.email;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "https://putamirrorservice.loca.lt/api/status?email="+email, true);
        xhr.setRequestHeader("Bypass-Tunnel-Reminder", "true");
        xhr.onreadystatechange = function()
        {
            if(xhr.readyState == XMLHttpRequest.DONE)
            {
                JSONObj = (xhr.response == null) ? null : JSON.parse(xhr.response);
                console.log(JSONObj);
                sendResponse({JSON: JSONObj});
            }
        }
        xhr.send();
        return true;
    }

    if(request.action == "checkExisting") {
        email = request.email;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "https://putamirrorservice.loca.lt/api/checkExisting?email="+email, true);
        xhr.setRequestHeader("Bypass-Tunnel-Reminder", "true");
        xhr.onreadystatechange = function()
        {
            if(xhr.readyState == XMLHttpRequest.DONE)
            {
                result = xhr.responseText;
                console.log(result);
                sendResponse({Result: result});
            }
        }
        xhr.send();
        return true;
    }
    if(request.action == "deleteDownload") {
        email = request.email;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "https://putamirrorservice.loca.lt/api/delete?email="+email, true);
        xhr.setRequestHeader("Bypass-Tunnel-Reminder", "true");
        xhr.onreadystatechange = function()
        {
            if(xhr.readyState == XMLHttpRequest.DONE)
            {
                result = xhr.responseText;
                sendResponse({Result: result});
            }
        }
        xhr.send();
        return true;
    }
});

