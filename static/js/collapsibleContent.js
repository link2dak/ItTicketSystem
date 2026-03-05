//checks if a button is clicked and togles the content of it
    const wrapper = document.querySelector('.ticket-wrapper');
    const collList = wrapper.querySelectorAll('.collapsible');
    const conList = wrapper.querySelectorAll('.content')

    for (const className of collList) {
        //checks if the button was most currently added and displays it as if it was clicked
            console.log(className.dataset.state)
            if(className.dataset.state === "active"){
                click(className, conList, Array.from(collList).indexOf(className));
            
                //makes the state inactive again
                className.dataset.state = "inactive";
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


//make the delete button appear when a checkbox is selected
const checkBoxes = document.querySelectorAll('input[type="checkbox"][name="checkbox"]');
const deleteButton = document.getElementById('deleteButton');
console.log(checkBoxes)



    for (const checkbox of checkBoxes){
        checkbox.addEventListener('click', function(){
            var boolean = false;
            //checks to see if there are any other 
            for(check of checkBoxes){
                if(check.checked){
                    boolean = true;
                }
            }
            if(checkbox.checked){
                deleteButton.style.display = 'block';
            }
            else if(!boolean){
                deleteButton.style.display = 'none';
            }
        })
    }