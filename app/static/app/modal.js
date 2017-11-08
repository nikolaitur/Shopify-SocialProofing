  console.log("Enter this block.");
  alert("Hey youre here");
  var para = document.createElement("p");
  var node = document.createTextNode("This is new.");

  para.appendChild(node);

  var element = document.getElementById("MainContent");
  element.appendChild(para);
