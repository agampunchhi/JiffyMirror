if(window.location.href.indexOf('mirror.html') > -1) {
dropButton = document.getElementById('dropbtn');
dropButton.addEventListener('mouseover', function() {
chrome.storage.local.get('folderArray', data => {
    if(data.folderArray != null && data.folderArray != "") {
        contentDiv = document.getElementById('content');
        contentDiv.innerHTML = '';
        data.folderArray.forEach(folderID => {
            button = document.createElement('button');
            button.innerHTML = folderID;
            button.addEventListener('click', function() {
                document.getElementById("folderID").value= folderID;
            });
            contentDiv.appendChild(button);
        });
        savedFolder = document.createElement('button');
        savedFolder.innerHTML = 'Edit Saved Folders';
        savedFolder.addEventListener('click', function() {
                window.location.assign("../pages/savedFolders.html");
            });
        contentDiv.appendChild(savedFolder);
    }
    else {
        contentDiv = document.getElementById('content');
        contentDiv.innerHTML = '';
        savedFolder = document.createElement('span');
        savedFolder.innerHTML = "No folders saved";
        contentDiv.appendChild(savedFolder);

    }
});
});
}
