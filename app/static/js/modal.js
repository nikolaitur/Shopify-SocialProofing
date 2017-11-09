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
    document.head.appendChild(script);
  }());
