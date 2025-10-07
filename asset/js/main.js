var mcqValidationListener = function(event) {
    console.log("listening to checkbox")
    const checkboxes = document.querySelectorAll('input[name="mcq_answers"]');
   
    const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    if (!isChecked) {
        event.preventDefault();  // Prevent form submission
        alert("Please select at least one option.");
    }
    
}

var tfValidationListener = function(event) {
    console.log("listening to radio")
    const radioButtons = document.querySelectorAll('input[name="tf_answers"]');
  
        const isChecked = Array.from(radioButtons).some(radio => radio.checked);

        if (!isChecked) {
            event.preventDefault();  // Prevent form submission
            alert("Please select True or False.");
        }
    
}

function checkboxValidation(){
  
    console.log('in function')
    // Add an event listener to validate when the form is submitted
    document.getElementById('ques_form').addEventListener('submit', mcqValidationListener);
}

function radioValidation(){
    console.log('in function')
    document.getElementById('ques_form').addEventListener('submit', tfValidationListener);
}

function removePreviousListeners() {
    if (mcqValidationListener) {
        document.getElementById('ques_form').removeEventListener('submit', mcqValidationListener);
    }
    if (tfValidationListener) {
        document.getElementById('ques_form').removeEventListener('submit', tfValidationListener);
    }
}


function quesTypeSwitch(){
    document.addEventListener("DOMContentLoaded", function() {
        const questionTypeDropdown = document.getElementById("id_question_type");
    
        questionTypeDropdown.addEventListener("change", function() {
            // Hide all conditional fields
            document.querySelectorAll(".conditional-div").forEach(field => {
                field.style.display = "none";
            });
            
            // Show the relevant field based on selected option
            const selectedType = questionTypeDropdown.value;
            if (selectedType === "mcq") {
                document.getElementById("mcq_div").style.display = "block";
                
                // Remove previous event listeners
                removePreviousListeners() 
                checkboxValidation()
            } 
            else if (selectedType === "essay") {
                document.getElementById("essay_div").style.display = "block";
                removePreviousListeners() 
            } 
            else if (selectedType === "tf") {
                document.getElementById("tf_div").style.display = "block";

                // Remove previous event listeners
                removePreviousListeners() 
                radioValidation();
            }
        });
    
        // Display initially selected option if available (useful for edit page)
        const initialType = questionTypeDropdown.value;
        if (initialType) {
            questionTypeDropdown.dispatchEvent(new Event("change"));
        }
    });
}

function confirm_delete(){
    return confirm("Are you sure you want to delete this question?");
}

function show_exam_setting(){
    // Get references to the button and the div
    console.log("Show exam")
    const exam_div = document.getElementById("exam_div");

    if (exam_div.style.display === "none" || exam_div.style.display === "") {
        exam_div.style.display = "block";  // Show the div
    } else {
        exam_div.style.display = "none";   // Hide the div
    }
}
