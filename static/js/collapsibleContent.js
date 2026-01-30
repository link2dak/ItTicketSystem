//checks if a button is clicked and togles the content of it
    var coll = document.getElementsByClassName("collapsible");
    var i;
    for (i = 0; i < coll.length; i++) {
        //checks if the button was most currently added and displays it as if it was clicked
        if(coll[i].dataset.state === "active"){
            var content = coll[i].nextElementSibling;
            console.log("there has been a match for active")
            coll[i].classList.toggle("active")
            content.style.display = "block";

            coll[i].dataset.state = "inactive";
        }
        
        console.log(coll[i].dataset.state)
        coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
        content.style.display = "none";
        } else {
        content.style.display = "block";
        }
    });   
}