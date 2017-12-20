// 1. StoreSettings data
// 1a. Product Last Ordered 23 hours old
// 1b. # of customers who ordered
// mystore.shopify.com/120392
// { lastName: 'Liou' }
// storesettings


(function () {
  //Logic for the modal library
  var api = {
    start: function () {
      //Get the *.myshopify.com domain
      var shop = Shopify.shop;
      var product = meta.product.id;
      api.fetchSettingsFromAPI(shop, product)
    },
    fetchSettingsFromAPI: function (shop, product) {
      if (window.location.href.includes('michael-john-devs') || window.location.href.includes('ellie-designer-clothing') || window.location.href.includes('new-store-qa')) {
        // Test app url
        url = 'https://protected-reef-37693.herokuapp.com/api/modal/' + shop + '/' + product
      } else {
        // Production app url
        url = 'https://socialproof-samurai.herokuapp.com/api/modal/' + shop + '/' + product
      }
      console.log(url);
      fetch(url)
      .then(function(response) {
        response.json().then(function(data) {
          if (!data || !api.validateData(data)) {
            return;
          }
          var settings = data;
          api.renderModal(settings)
        });
      })
      .catch(function(err) {
        console.log('Fetch Error :-S', err);
      });
    },
    validateData: function(data) {
      // Various checks to ensure a valid modal is rendered
      // Returning false will make the modal not render
      console.log("Data to parse is this ", data)

      if (!data.product_name) {
        console.log('No product name');
        return false;
      }

      if (data.social_setting == "latest") {
        if (!data.processed_at) {
          console.log('no one bought the item within the lookback look_back_period');
          return false;
        }
        if (!data.first_name || !data.last_name) {
          console.log('first or last name not provided for order');
          return false;
        }
      }

      if (data.social_setting == "purchase") {
        if (!data.qty_from_look_back) {
          console.log('no items were sold within lookback period');
          return false;
        }
      }

      return true;
    },
    modalAnimation: function () {
      $(document).ready(function() {
        $("#modal").animate({"opacity": "1"},2500);
      });
    },
    renderModal: function(settings) {
      // Set up main modal elements
      var modal = document.createElement("div");
      var imageNode = document.createElement("div");
      var specialTextNode = document.createElement("p");
      var timestampTextNode = document.createElement("p");
      var productNameTextNode = document.createElement("a");

      modal.id = "modal";
      imageNode.id = "product-image";
      specialTextNode.id = "modal-special-text";
      timestampTextNode.id = "timestamp-text";
      productNameTextNode.id = "product-name-text";

      document.body.appendChild(modal);
      modal.appendChild(imageNode);
      modal.appendChild(specialTextNode);
      modal.appendChild(timestampTextNode);
      modal.appendChild(productNameTextNode);

      api.renderModalText(settings); // Description
      api.renderImage(settings.main_image_url); // adding product image
      api.renderClose(); // Make the x close button
      api.addStyles(); // Add styles
      //specific style for diff location
      if (settings.location === "lower-right") {
        $("#modal").css({"left": "", "right": "2%"});
      }
      api.modalAnimation();
      api.clickMetrics(settings.product_id);  // adding click handler to track metrics of how many people clicked.
    },
    renderImage: function(imageUrl) {
      var img = $('<img id="image">');
      img.attr('src', imageUrl);
      img.appendTo('#product-image');
    },
    convertDaysToTimestampText: function(days) {
      // Returns days to timestamp text and floors it and units
      var units = "";
      var convertedTime = "";
      console.log(days);
      if (days * 24 < 1) {
        convertedTime = days*24*60;
        units = "minutes";
        console.log("Difference less than 1 hour. Convert minutes.");
      } else if (days < 1) {
        convertedTime = days*24;
        units = "hours";
        console.log("Difference less than 1 day. Convert hours.");
      } else {
        convertedTime = days;
        units = "days";
        console.log("Difference greater than 1 day. Keep days.");
      }
      convertedTime = Math.floor(convertedTime);

      if (convertedTime == 1) {
        units = units.replace("s", "");
      }

      return {
        convertedTime: convertedTime,
        units: units
      };
    },
    renderModalText: function (data) {
      var modalSpecialText = "";
      var timestampText = "";
      var productNameText = data.product_name;

      var specialTextNode = document.getElementById("modal-special-text");
      var timestampTextNode = document.getElementById("timestamp-text");
      var imageNode = document.getElementById("product-image");
      var productNameTextNode = document.getElementById("product-name-text");

      // --------------- Modal Special Text Logic --------------------------- //

      if (data.social_setting == "latest") {
        var first_name = data.first_name;
        var last_name = data.last_name;
        var province = data.province_code;
        var processedAtDateTime = new Date(data.processed_at);
        var nowDateTime = new Date();
        var differenceDays = (nowDateTime-processedAtDateTime)/1000/60/60/24; // days

        modalSpecialText = first_name + " " + last_name + " purchased a";
        convertedTimeObj = api.convertDaysToTimestampText(differenceDays);
        timestampText = convertedTimeObj.convertedTime + " " + convertedTimeObj.units + " ago"
      } else {
        // Default to "purchase" social_setting as fallback
        if (data.last_order_qty == 1) {
          modalSpecialText = data.last_order_qty + " person purchased";
        } else {
          modalSpecialText = data.last_order_qty + " people purchased";
        }
        convertedTimeObj = api.convertDaysToTimestampText(data.look_back/24);

        if (convertedTimeObj.convertedTime != 1) {
            timestampText = "Past " + convertedTimeObj.convertedTime + " " + convertedTimeObj.units;
        } else {
          // "Past hour"
          timestampText = "Past " + convertedTimeObj.units;
        }
      }

      // Only add redirect link if different product
      if (meta.product.id != data.product_id) {
        console.log("Not same product id, so I add redirect link to modal.");
        var productLink = "https://" + data.store_name + "/products/" + data.handle;
        productNameTextNode.href = productLink;
        $("#product-image").wrap($("<a>").attr("href", productLink));
      }
      timestampTextNode.appendChild(document.createTextNode(timestampText));
      productNameTextNode.appendChild(document.createTextNode(productNameText));
      specialTextNode.appendChild(document.createTextNode(modalSpecialText));
    },
    // if the special text node is clicked, then add this functionality.
    clickMetrics: function (productTo) {
      $(document).ready(function(){
        var shop = Shopify.shop;
        var productFrom = meta.product.id;
        if (window.location.href.includes('michael-john-devs') || window.location.href.includes('ellie-designer-clothing') || window.location.href.includes('new-store-qa')) {
          // Test app url
          url = 'https://protected-reef-37693.herokuapp.com/api/modal/' + shop + '/' + product
        } else {
          // Production app url
          url = 'https://socialproof-samurai.herokuapp.com/api/modal/' + shop + '/' + product
        }
        console.log(url);

        $("#product-name-text, #image").click(function(e){
          $.ajax({type: "POST",
                  url: url,
                  data: { store_name: shop, product_id_to: productTo, product_id_from: productFrom},
                  success:function(){
                    console.log("Post was successful ", shop, productTo, productFrom);
                  }
                });
              });
        })
    },
    renderClose: function () {
      var close = document.createElement("span");
      var x = document.createTextNode("x");
      close.appendChild(x)
      close.id = "close"
      var modal = document.getElementById("modal");
      modal.appendChild(close)
      $(function() {
        $("#close").click(function() {
          $("#modal").animate({"opacity": "0"},800);
          setTimeout( function(){
            $('#modal').css('display','none');
          },800);
        });
      });
    },
    addStyles: function () {
      var modal = document.getElementById("modal");
      var imageContainer = document.getElementById("product-image");
      var image = document.getElementById("image");
      var specialText = document.getElementById("modal-special-text");
      var productNameText = document.getElementById("product-name-text");
      var timestampText = document.getElementById("timestamp-text");
      var close = document.getElementById("close");

      var modalStyles = {
        width: "350px",
        height: "70px",
        display: "block",
        position: "fixed",
        bottom: "2%",
        left: "2%",
        backgroundColor: "white",
        boxShadow: "0 0 5px #888",
        opacity: "0"
      }

      var imageContainerStyles = {
        width: "35%",
        position: "relative",
        margin: "0 5px 0 0"
      }

      var imageStyles = {
        width: "auto",
        border: "0",
        maxHeight: "70px"
      }

      var specialTextStyles = {
        position: "absolute",
        width: "75%",
        top: "0",
        left: "30%",
        right: "20px",
        fontFamily: "Tahoma",
        fontSize: "14px",
        color: "#1A6BCA"
      }

      var productNameTextStyles = {
        position: "absolute",
        width: "75%",
        top: "20px",
        left: "30%",
        right: "20px",
        fontFamily: "Tahoma",
        fontWeight: "bold",
        fontSize: "15px"
      }

      var timestampTextStyles = {
        position: "absolute",
        width: "75%",
        left: "75%",
        top: "50px",
        right: "10px",
        fontFamily: "Tahoma",
        fontSize: "12px",
        color: "#1A6BCA"
      }

      var closeStyles = {
        position: "absolute",
        top: "0",
        right: "5px",
        cursor: "pointer",
        fontFamily: "Tahoma",
        fontSize: "14px"
      }

      for (var key in modalStyles) {
        modal.style[key] = modalStyles[key];
      }
      for (var key in imageContainerStyles) {
        imageContainer.style[key] = imageContainerStyles[key]
      }
      for (var key in imageStyles) {
        image.style[key] = imageStyles[key]
      }
      for (var key in specialTextStyles) {
        specialText.style[key] = specialTextStyles[key]
      }
      for (var key in productNameTextStyles) {
        productNameText.style[key] = productNameTextStyles[key]
      }
      for (var key in timestampTextStyles) {
        timestampText.style[key] = timestampTextStyles[key]
      }
      for (var key in closeStyles) {
        close.style[key] = closeStyles[key]
      }
    }
  }
  //Starting it off
  if (meta.page.pageType === "product") {
    console.log("This is a product good to go good to go")
    api.start();
  }
}());
