if(window.location.href.indexOf('status.html') > -1) {
    backBttn = document.getElementById("backBttn");
    backBttn.addEventListener("click", function() {
        window.location.replace("../pages/mirror.html");
    });
    cancelBttn = document.getElementById("cancel");
    cancelBttn.addEventListener("click", function() {
        chrome.storage.local.get('email', function(data) {
        chrome.runtime.sendMessage({
            action: "deleteDownload",
            email: data.email
        });
    });
    });
}
function getStatus() {
    chrome.storage.local.get('email', function(data) {
        if(data.email != null) {
            console.log('email: ' + data.email);
            email = data.email;
            chrome.runtime.sendMessage({
                action: "statusFetch",
                email: email
            }, function(response) {
                if(response.JSON != null) {
                    listParent = document.getElementById("List");
                    jsonObject = response.JSON
                    listParent.innerHTML = "";
                    jsonStr = JSON.stringify(jsonObject);
                    if(jsonStr != '[]')
                    {
                    jsonObject.forEach(function(task) {
                        listChild = document.createElement("li");
                        listChild.className = "List";
                        titleDiv = document.createElement("div");
                        titleDiv.className = "ListDiv";
                        titleDiv.innerText = task.title;
                        statsDiv = document.createElement("div");
                        statsDiv.className = "ListDiv";
                        if(task.failed == 'True') {
                        statsDiv.innerText = "Failed"; }
                        else if(task.completed == 'True' && task.failed == 'False' && task.uploaded == 'False') {
                        statsDiv.innerText = "Uploading"; }
                        else if(task.completed == 'True' && task.uploaded == 'True') {
                        linkElement = document.createElement("a");
                        linkElement.href = task.gDriveLink;
                        linkElement.target = "_blank";
                        linkBttn = document.createElement("button");
                        linkBttn.className = "openBttn";
                        linkBttn.innerText = "Open";
                        linkElement.appendChild(linkBttn);
                        statsDiv.appendChild(linkElement);
                        }
                        else {
                        statsDiv.innerText = "Progress: "+task.percentage+" Size: "+task.size+"";}
                        time = task.time;
                        speed = task.speed;
                        timeSpeedDiv = document.createElement("div");
                        timeSpeedDiv.className = "ListDiv";
                        if(time == "999999999 days, 23:59:59.999999"){
                            time = "ETA";
                        }
                        timeSpeedDiv.innerText = "Time: "+time+" Speed: "+speed+"";
                        listChild.appendChild(titleDiv);
                        listChild.appendChild(statsDiv);
                        if(task.completed == 'False' && task.failed == 'False') { 
                        listChild.appendChild(timeSpeedDiv);
                        }
                        listParent.appendChild(listChild);
                    });
                } else {
                    listChild = document.createElement("li");
                    listChild.className = "List";
                    listChild.style.borderStyle = "none"
                    titleDiv = document.createElement("div");
                    titleDiv.className = "ListDiv";
                    titleDiv.innerText = "No Active Tasks";
                    listChild.appendChild(titleDiv);
                    listParent.appendChild(listChild);
                }
                }
            });
        }
    });
}
if(window.location.href.indexOf('status.html') > -1) {
    getStatus();
    setInterval(function() {
        getStatus();
}, 3000);
}
