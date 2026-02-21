//checks if a button is clicked and togles the content of it
    // var coll2 = document.getElementsByClassName("collapsible");
    const wrapper = document.querySelector('.ticket-wrapper');
    const collList = wrapper.querySelectorAll('.collapsible');
    const conList = wrapper.querySelectorAll('.content')

    for (const className of collList) {
        //checks if the button was most currently added and displays it as if it was clicked
            console.log(className.dataset.state)
            if(className.dataset.state === "active"){
            var content = collList[Array.from(collList).indexOf(className)].nextElementSibling;
            console.log("there has been a match for active")
            collList[i].classList.toggle("active")
            content.style.display = "block";
            
            //makes the state inactive again
            collList[i].dataset.state = "inactive";
        }
        className.addEventListener("click", () => click(className, conList, Array.from(collList).indexOf(className)));
}   


function click(name, con, index){
        name.classList.toggle("active");
        var content = con[index];
        console.log(name.length + "this is the class list")
        if (content.style.display === "block") {
        content.style.display = "none";
        } else {
        content.style.display = "block";
        }
}