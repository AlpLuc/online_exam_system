function showExamSetting(){

    document.getElementById("exam_div").style.display = "block";
    document.getElementById("tracking_div").style.display = "none";
    
    document.getElementById("exam_btn").classList.add('btn-primary');
    document.getElementById("tracking_btn").classList.remove('btn-primary');
}

function showTrackingSetting(){
    document.getElementById("exam_div").style.display = "none";
    document.getElementById("tracking_div").style.display = "block";

    document.getElementById("exam_btn").classList.remove('btn-primary');
    document.getElementById("tracking_btn").classList.add('btn-primary')
}

function markTrackingPressed(){
    document.getElementById('tracking_btn').setAttribute('data-pressed', 'true');
}

function checkTrackingStatus(event){
    const trackingButton = document.getElementById('tracking_btn');
    if (trackingButton.getAttribute('data-pressed') === 'true') {
        console.log("Tracking Setting button has been pressed.");
    } else {
        confirmTracking = confirm("Do you make changes to the Exam Tracking Settings before submitting?");
        if (confirmTracking) {
            // Run a function or logic if the user confirms
            showTrackingSetting(); // Optionally mark it as pressed or handle other logic
            markTrackingPressed();
            event.preventDefault();
        }
        else{
            markTrackingPressed();
        }
    }
}

function questionBankChangeConfirm(){
    const questionBankSelect = document.getElementById('id_question_bank');
    questionBankSelect.setAttribute('data-prev-id', questionBankSelect.value);

    document.getElementById('id_question_bank').addEventListener('change', function() {
        const questionBankId = this.value;
        const prevQuestionBankId = this.getAttribute('data-prev-id');
        console.log("Previous question bank:", prevQuestionBankId);
        console.log("New question bank:", questionBankId);

        if (prevQuestionBankId == "") {
            // If "Select a Question Bank" is chosen, directly load the empty question list
            getQuestionList(questionBankId);
            this.setAttribute('data-prev-id', questionBankId);
        } 
        else if (prevQuestionBankId !== "" && questionBankId !== prevQuestionBankId){
        // Show confirmation dialog only if a specific question bank is selected
        const confirmChange = confirm("Changing the question bank will clear the existing question list. Do you want to proceed?");
        
        if (confirmChange) {
            // Clear question list if user confirms
            document.getElementById('ques_tbody').innerHTML = '';
            getQuestionList(questionBankId);   
            this.setAttribute('data-prev-id', questionBankId);
        }
        else{
            getQuestionList(prevQuestionBankId)
        }
    }
    });
}

function validateCheckboxes() {
    const checkboxes = document.querySelectorAll('input[name="selected_questions"]');
    const atLeastOneChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

    console.log('Validating checkbox')
    
    if (!atLeastOneChecked) {
        const question_div = document.getElementById('ques_div');   
        // Trigger the popover
        question_div.setAttribute('data-bs-content', 'Please select at least one question.');
        const popover = new bootstrap.Popover(question_div);
        popover.show();
        
        setTimeout(() => {
            popover.hide();
        }, 3000);
        // Prevent form submission
        return false;
    }
    else{
        return true; // Allow form submission
    }   
}

function validateDateTime() {
    const start_date_time = document.getElementById("id_start_date_time").value;
    const end_date_time = document.getElementById("id_end_date_time").value;

    console.log(start_date_time);
    console.log(end_date_time);

    if (new Date(end_date_time) <= new Date(start_date_time)) {
        // Trigger popover for the end date time field
        const popoverField = document.getElementById("id_end_date_time");
        popoverField.setAttribute('data-bs-content', 'End date and time must be later than the start date and time.');
        const popover = new bootstrap.Popover(popoverField);
        popover.show();

        setTimeout(() => {
            popover.hide();
        }, 3000);

        return false; // Stop further processing
    }

    return true; // Allow form submission if validation passes
}

function validate(){
    document.getElementById('submitBtn').addEventListener('click', function(event){
        if(!validateCheckboxes() || !validateDateTime()){
            event.preventDefault();
        }        
    });
}

function confirm_delete(event){
    event.stopPropagation();

    const userConfirmed = confirm("Are you sure you want to delete this exam?");
        
    if (!userConfirmed) {
        event.preventDefault(); // Prevent delete action.
    }
}

// Function to handle tab switch checkbox change
function checkTabSwitchCheckBox(checkbox, input) {
    if (checkbox.checked) {
        // Enable the input
        input.disabled = false;
    } else {
        // Disable the input and reset to default value of 0
        input.disabled = true;
        input.value = 1;
    }
}

function toggleTabSwitchLimit(){
    // Get the checkbox and input elements
    const tabSwitchCheckbox = document.getElementById("id_tab_switch");
    const tabSwitchLimitInput = document.getElementById("id_tab_switch_limit");
    console.log(tabSwitchCheckbox)
    // Attach event listener to the checkbox
    tabSwitchCheckbox.addEventListener("change", function() {
        checkTabSwitchCheckBox(tabSwitchCheckbox, tabSwitchLimitInput);
    });

    // Initialize the default state
    checkTabSwitchCheckBox(tabSwitchCheckbox, tabSwitchLimitInput);
}

function toggleAllCheckboxes(masterCheckbox) {
    const checkboxes = document.querySelectorAll('.question_checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = masterCheckbox.checked;
    });
}

function updateCheckAllStatus() {
    // Get the select all checkbox
    const checkAll = document.getElementById('checkAll');
    // Get all individual checkboxes
    const checkboxes = document.querySelectorAll('.question_checkbox');
    // Check if all checkboxes are selected
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);

    console.log(allChecked)

    // Update the master checkbox
    if (allChecked) {
        checkAll.checked = true;
    } else {
        checkAll.checked = false;
    }   
}