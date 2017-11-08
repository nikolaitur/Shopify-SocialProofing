  (function () {
  	//Build a pseudo-class to prevent polluting our own scope.
    console.log("Enter this block.");
    alert("Hey youre here");
    var para = document.createElement("p");
    var node = document.createTextNode("This is new.");

    para.appendChild(node);

    var element = document.getElementById("MainContent");
    element.appendChild(para);
    
    var script = document.createElement("script");
    script.src = "https://protected-reef-37693.herokuapp.com/app/static/js/modal.js";
    document.head.appendChild(script);
  }());