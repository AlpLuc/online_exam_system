var mcqValidationListener = function(event) {
    console.log("listening to checkbox");
    const checkboxes = document.querySelectorAll('input[name="mcq_answers"]');
   
    const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
    if (!isChecked) {
        event.preventDefault();  // Prevent form submission
        alert("Please select at least one option.");
    }
    else{
        document.getElementById("id_question_bank").disabled = false;   //enable question bank
    }
}

var mcqOptionValidationListener = function(event) {
    console.log("listening to option");
    const options = document.querySelectorAll('input[name="options"]');
   
    const allFilled = Array.from(options).every(option => option.value.trim() !== "");

    if (!allFilled) {
        event.preventDefault();  // Prevent form submission
        alert("Please fill up all the options.");
    }
    else{
        document.getElementById("id_question_bank").disabled = false;   //enable question bank
    }
}

var tfValidationListener = function(event) {
    console.log("listening to radio");
    const radioButtons = document.querySelectorAll('input[name="tf_answers"]');
  
        const isChecked = Array.from(radioButtons).some(radio => radio.checked);

        if (!isChecked) {
            event.preventDefault();  // Prevent form submission
            alert("Please select True or False.");
        }
        else{
            document.getElementById("id_question_bank").disabled = false;   //enable question bank
        }
}

var submitListener = function(event) {
    document.getElementById("id_question_bank").disabled = false;
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

function optionValidation(){
    console.log('in function')
    document.getElementById('ques_form').addEventListener('submit', mcqOptionValidationListener);
}

function enableSelectOnSubmit(){
    console.log('in function')
    document.getElementById('ques_form').addEventListener('submit', submitListener);
}

function removePreviousListeners() {
    if (mcqValidationListener) {
        document.getElementById('ques_form').removeEventListener('submit', mcqValidationListener);
    }
    if (tfValidationListener) {
        document.getElementById('ques_form').removeEventListener('submit', tfValidationListener);
    }
    if (mcqOptionValidationListener){
        document.getElementById('ques_form').removeEventListener('submit', mcqOptionValidationListener);
    }
    if (submitListener){
        document.getElementById('ques_form').removeEventListener('submit', submitListener);
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
                removePreviousListeners(); 
                checkboxValidation();
                optionValidation();
            } 
            else if (selectedType === "essay") {
                document.getElementById("essay_div").style.display = "block";
                removePreviousListeners();
                enableSelectOnSubmit();
            } 
            else if (selectedType === "tf") {
                document.getElementById("tf_div").style.display = "block";

                // Remove previous event listeners
                removePreviousListeners(); 
                radioValidation();
            }
        });
    
        // Display initially selected option if available
        const initialType = questionTypeDropdown.value;
        if (initialType) {
            questionTypeDropdown.dispatchEvent(new Event("change"));
        }
    });
}

function confirmDelete(event){
    const userConfirmed = confirm("Are you sure you want to delete this question?");
        
    if (!userConfirmed) {
        event.preventDefault(); // Prevent delete action.
    } 
}
