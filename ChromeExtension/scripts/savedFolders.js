if(window.location.href.indexOf("savedFolders.html") > -1) {
    chrome.storage.local.get('folderArray', data => {
        if(data.folderArray != null) {
            var folderArray = data.folderArray
            var folderList = document.getElementById("List")
            folderArray.forEach(folder => {
                var li = document.createElement("li")
                li.className = "List"
                var div = document.createElement("div")
                div.className = "ListDiv"
                var span = document.createElement("span")
                span.className = "ListSpan"
                var removeBttn = document.createElement("button")
                removeBttn.className = "removeBttn"
                removeBttn.innerHTML = "X"
                div.appendChild(span)
                div.appendChild(removeBttn)
                li.appendChild(div)
                folderList.appendChild(li)
                removeBttn.addEventListener("click", () => {
                    folderList.removeChild(li)
                    folderArray.splice(folderArray.indexOf(folder), 1)
                    chrome.storage.local.set({'folderArray': folderArray})
                });
                span.innerHTML = folder

                
            })
        }
    })
}

if(window.location.href.indexOf("savedFolders.html") > -1) {
    backBttn = document.getElementById("backBttn");
    backBttn.addEventListener("click", function() {
        window.location.replace("../pages/mirror.html");
    });
}
