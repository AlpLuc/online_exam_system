function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//Flag Questions
function flagQuestion(type, question_element_id, btn_element_id, question_number){
    btn_element = document.getElementById(btn_element_id);
    question_element = document.getElementById(question_element_id);

    if(question_element.style.display == "none"){
        btn_element.classList.remove('btn-light');
        btn_element.classList.add('btn-danger');
        question_element.style.display = "block";

        // Add question to flagged list
        if (!flagged_question_dict[type]) {
            flagged_question_dict[type] = [];
        }
        if (!flagged_question_dict[type].includes(question_number)) {
            flagged_question_dict[type].push(question_number);
        }
        postFlaggedQuestions()
    }
    else{
        btn_element.classList.remove('btn-danger');
        btn_element.classList.add('btn-light');
        question_element.style.display = "none";

        if (flagged_question_dict[type]) {
            flagged_question_dict[type] = flagged_question_dict[type].filter(id => id !== question_number);
        }
        postFlaggedQuestions()
    }

    console.log(flagged_question_dict)

    function postFlaggedQuestions() {
        fetch('/exam/save_flagged_questions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ flagged_question_dict }),
        }).catch(error => console.error('Error:', error));
    }
}

function initiateFlaggedQuestion(flagged_questions){
    for (const key in flagged_questions) {
        if (flagged_questions.hasOwnProperty(key)) {
            type = key;
            flagged_questions[key].forEach(item => {
                question_element_id = key + '_flag_' + item;
                btn_element_id = key + '_flag_btn_' + item;

                btn_element = document.getElementById(btn_element_id);
                question_element = document.getElementById(question_element_id);

                btn_element.classList.remove('btn-light');
                btn_element.classList.add('btn-danger');
                question_element.style.display = "block";
            });
        }
    }
}

//Countdown timer
function startCountdown(initialTime) {
    const timerDisplay = document.getElementById('timer');
    let timeRemaining = initialTime;

    updateTimerDisplay(timeRemaining);

    const countdownInterval = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay(timeRemaining);

        if(timeRemaining <= 600){
            document.getElementById("timer").classList.add('text-danger')
        }

        //Check if time is up, if yes, redirect, if not save timer
        if (timeRemaining < 1) {
            clearInterval(countdownInterval);
            document.getElementById('examination_form').submit();
        }
        // Save the remaining time to the server every minute
        else if (timeRemaining % 1 === 0) {
            saveTimerToServer(timeRemaining);
        }

    }, 1000);

    //Update timer every second
    function updateTimerDisplay(time) {
        const minutes = Math.floor(time / 60);
        const seconds = time % 60;
        timerDisplay.textContent = `${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
    }
    //save timer to session
    function saveTimerToServer(remainingTime) {
        fetch('/exam/save_timer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ remaining_time: remainingTime })
        }).then(response => {
            if (!response.ok) {
                console.error('Failed to save timer');
            }
            else if(response.ok){
                console.log('success')
            }
        });
    }
}

//Displa/hide question div
function showMCQ(){
    if (document.getElementById("mcq_question_div")){
        document.getElementById("mcq_question_div").style.display = "block";
        document.getElementById("mcq_tab").classList.add('active');
        document.getElementById("mcq_btn").classList.add('active');
    }

    if (document.getElementById("tf_question_div")){
        document.getElementById("tf_question_div").style.display = "none";
        document.getElementById("tf_tab").classList.remove('active');
        document.getElementById("tf_btn").classList.remove('active');
    }
    
    if (document.getElementById("essay_question_div")){
        document.getElementById("essay_question_div").style.display = "none";
        document.getElementById("essay_tab").classList.remove('active');
        document.getElementById("essay_btn").classList.remove('active');
    }
}

function showTF(){
    if (document.getElementById("mcq_question_div")){
        document.getElementById("mcq_question_div").style.display = "none";
        document.getElementById("mcq_tab").classList.remove('active');
        document.getElementById("mcq_btn").classList.remove('active');
    }

    if (document.getElementById("tf_question_div")){
        document.getElementById("tf_question_div").style.display = "block";
        document.getElementById("tf_tab").classList.add('active');
        document.getElementById("tf_btn").classList.add('active');
    }
    
    if (document.getElementById("essay_question_div")){
        document.getElementById("essay_question_div").style.display = "none";
        document.getElementById("essay_tab").classList.remove('active');
        document.getElementById("essay_btn").classList.remove('active');
    }
}

function showEssay(){
    if (document.getElementById("mcq_question_div")){
        document.getElementById("mcq_question_div").style.display = "none";
        document.getElementById("mcq_tab").classList.remove('active');
        document.getElementById("mcq_btn").classList.remove('active');
    }

    if (document.getElementById("tf_question_div")){
        document.getElementById("tf_question_div").style.display = "none";
        document.getElementById("tf_tab").classList.remove('active');
        document.getElementById("tf_btn").classList.remove('active');
    }
    
    if (document.getElementById("essay_question_div")){
        document.getElementById("essay_question_div").style.display = "block";
        document.getElementById("essay_tab").classList.add('active');
        document.getElementById("essay_btn").classList.add('active');
    }
}

//Scroll to top button function
function scrollToTop() {
    window.scrollTo(0, 0);
}

//Save answer to session
function sessionSaveSelectedAnswers(){
    const mcq_answers = {};
    const tf_answers = {};
    const essay_answers = {};

    //MCQ slected answers
    const checkboxes = document.querySelectorAll(".mcq_checkbox");
    checkboxes.forEach((checkbox) => {
        const questionId = checkbox.getAttribute("data-question-id");
        
        if (!mcq_answers[questionId]) {
            mcq_answers[questionId] = [];
        } 

        if (checkbox.checked) { // Only consider checked checkboxes
            const questionId = checkbox.getAttribute("data-question-id");
            const value = checkbox.value;

            if (!mcq_answers[questionId].includes(value)) {
                mcq_answers[questionId].push(value);
            }
        }
    });

    //TF selected answers
    const radioButtons = document.querySelectorAll(".tf_radio");
    radioButtons.forEach((radioButton) => {
        const questionId = radioButton.getAttribute("tf-question-id");
        if (!tf_answers[questionId]) {
            tf_answers[questionId] = '';
        } 

        if (radioButton.checked) { // Only consider checked radio button
            const value = radioButton.value;
            tf_answers[questionId] = value;
        }
    });

    //Essay answers
    const textareas = document.querySelectorAll(".essay-textarea");
    textareas.forEach((textarea) => {
        const questionId = textarea.getAttribute("essay-question-id");
        const content = textarea.value;
        essay_answers[questionId] = content;
    });

    saveSelectedAnswerToServer(mcq_answers, tf_answers, essay_answers)

    function saveSelectedAnswerToServer(mcq_answers, tf_answers, essay_answers){
        const payload = {
            'mcq': mcq_answers,
            'tf': tf_answers,
            'essay': essay_answers, 
        };


        fetch('/exam/session_save_selected_answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        }).then(response => {
            if (!response.ok) {
                console.error('Failed to save selected answer');
            }
        }).catch(error => {
            console.error('Error saving selected answers:', error);
        });
    }
}

//Restrictions
function preventBrowserBack() {
    window.history.pushState(null, "", window.location.href);

    window.onpopstate = function() {
        alert("Restricted, Please finish the exam by clicking the Submit button on the bottom of the page");
        window.history.pushState(null, "", window.location.href);
        uploadBrowserActivityLog("Attempt to go to previous page", 1);
    };
}

function restrictCopyCutPaste(){
    console.log("Applying copy-paste restriction.");
    document.addEventListener("DOMContentLoaded", function () {
        document.addEventListener("copy", (event) => {
            event.preventDefault();
            alert("COPY ACTION DISABLED");
            uploadBrowserActivityLog("Attempt to copy", 1);
            unwated_behaviour = true;
        });

        document.addEventListener("cut", (event) => {
            event.preventDefault();
            alert("CUT ACTION DISABLED");
            uploadBrowserActivityLog("Attempt to cut", 1);
            unwated_behaviour = true;
        });

        document.addEventListener("paste", (event) => {
            event.preventDefault();
            alert("PASTE ACTION DISABLED");
            uploadBrowserActivityLog("Attempt to paste", 1);
            unwated_behaviour = true;
        });
    });
}

function restrictTabSwitching(tabSwitchCounter){
    document.addEventListener("DOMContentLoaded", function () {
        // Detect visibility changes using the Page Visibility API
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "hidden") {
                uploadBrowserActivityLog("Tab switched or minimized", 2);
            } else if (document.visibilityState === "visible") {
                uploadBrowserActivityLog("Tab active", 0);
            }
        });
        
        // Detect when window is not focused
        window.addEventListener("blur", () => {
            setTimeout(() => {
                    if (!document.hasFocus() && !is_picker_active) {
                        decrementTabSwitchCounter();
                        document.getElementById("tab_switch_alert_text").innerHTML = "The system has detected a tab switch action. Please stay on the exam page. <strong> Chances left: " + tabSwitchCounter + "</strong>";
                        tab_switch = true;
                        unwated_behaviour = true;

                        uploadBrowserActivityLog("Window lost focus", 2);
                }
            }, 50);
        });

        window.addEventListener("focus", () => {
            if(tab_switch){
                document.getElementById("tab_switch_alert").style.display = "block";
                tab_switch = false;
                unwated_behaviour = true;

                uploadBrowserActivityLog("Window regained focus", 0);
            }
        });
    });

    function decrementTabSwitchCounter(){
        if (tabSwitchCounter > 0){
            tabSwitchCounter--;

            fetch('/exam/update_tab_switch_counter/',{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({tab_switch_counter: tabSwitchCounter}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    console.log(data.message || "Tab switch counter updated successfully.");
                }
            })
            .catch(error => {
                console.error("Error updating tab switch counter:", error);
            });
        }
        else {
            document.getElementById('examination_form').submit(); 
        }


    }
}

function hide_tab_switch_alert(){
    document.getElementById("tab_switch_alert").style.display = "none";
}

async function startScreenCapture(exam_id) {
    let valid_capture = false;

    while (!valid_capture){
        try {
            is_picker_active = true;
            const stream = await navigator.mediaDevices.getDisplayMedia({
                video: { cursor: "always" },
                audio: false
            });


            // Extract video track
            const video_track = stream.getVideoTracks()[0];
            const track_settings = video_track.getSettings();

            const screen_capture_type = track_settings.displaySurface;

            // Validate capture type
            if (screen_capture_type !== "monitor") {
                alert("Please select the entire screen for the screen recording.");
                // Stop the current stream to allow user to reselect
                stream.getTracks().forEach(track => track.stop());
                valid_capture = false;
            }
            else {
                uploadBrowserActivityLog("Screen recording initiated", 0);
                window.focus();
                const modal = new bootstrap.Modal(document.getElementById('staticBackdrop'));
                modal.show();

                valid_capture = true;
                is_picker_active = false;

                recording_runnig = true;
                chunks = [];

                media_recorder = new MediaRecorder(stream, { mimeType: "video/webm; codecs=vp9" });

                media_recorder.ondataavailable = function (e) {
                    chunks.push(e.data);
                };

                media_recorder.onstop = function () {
                    if(unwated_behaviour || tab_switch){
                        actual_chunks = chunks.splice(0, chunks.length);
                        const blob = new Blob(actual_chunks, { type: "video/webm; codecs=vp9" });
                        uploadChunk(blob, exam_id); // Upload to server
                        unwated_behaviour = false;
                    }
                    else{
                        actual_chunks = chunks.splice(0, chunks.length);
                        console.log("No unwanted behavouir detected")
                    }
                };

                recordVideoChunk(stream);

                function recordVideoChunk(stream) {
                    media_recorder.start();

                    setTimeout(function() {
                        if(media_recorder.state == "recording")
                            media_recorder.stop();

                        if(recording_runnig)
                            recordVideoChunk(stream);
                    }, 10000); // 10 seconds videos
                
                }


                 // Detect when user stops screen sharing
                 video_track.onended = function() {
                    document.getElementById('examination_form').submit(); 
                };

            }
    
        } catch (err) {
            is_picker_active = false;
            console.error("Error starting screen capture:", err);
        }
    }
    return true;
}

function stopScreenCapture() {
    if (media_recorder && media_recorder.state !== "inactive") {
        console.log("Stops and upload");
        media_recorder.stop();
        media_recorder.onstop = function () {
            actual_chunks = chunks.splice(0, chunks.length);
            const blob = new Blob(actual_chunks, { type: "video/webm; codecs=vp9" });
            uploadChunk(blob, exam_id); // Upload to server
        };

        uploadBrowserActivityLog("Screen recording stopped", 0);
        console.log("MediaRecorder stopped.");
    }
    else {
        console.log("MediaRecorder is not active or already stopped.");
    }

    if (stream) {
        const tracks = stream.getTracks(); // Get all tracks (video, audio, etc.)
        tracks.forEach((track) => {
            track.stop(); // Stop each track
        });
        console.log("Screen capture stream stopped.");
    } 
    else {
        console.log("No active stream found to stop.");
    }
}

async function uploadChunk(chunk, exam_id) {
    console.log("Upload buffer chunk to server")
    uploadBrowserActivityLog("Upload screen recording", 0);
    const formData = new FormData();
    formData.append("chunk", chunk);

    path = "/exam/upload_screen_chunk/" + exam_id
    
    try {
        const response = await fetch(path, {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            throw new Error("Chunk upload failed");
        }
    } catch (err) {
        console.error("Error uploading chunk:", err);
    }

}

function uploadBrowserActivityLog(activity, status){
        console.log("Uploading_log");
        console.log(status);
        fetch('/exam/log_browser_activity/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Ensure you send CSRF token
            },
            body: JSON.stringify({ activity: activity, status: status})
        });
}

function logBrowserActivity(){
    detectIdle();
    detectResize(); //Could be triggere by resizing windows, open dev tools, or monitor chages
    detectPageReload();
    detectDevTool();
    detectWindowPosChange();
    detectNetworkConnectionLost();

}

function detectIdle(){
        let last_activity_time = new Date().getTime();
        let idle_status = false;
        let idle_time = 0;
        let idleInterval;
    
        idleInterval = setInterval(function (){
            idle_time++;
            checkIdleTime();
        }
        , 1000);
    
        function resetIdleTime() {
            if(idle_status){
                uploadBrowserActivityLog(`Idle duration: ${idle_time} seconds`, 1);
                idle_status = false;
            }
            idle_time = 0;
            last_activity_time = new Date().getTime();
        }
    
        function checkIdleTime() {
            const current_time = new Date().getTime();
            if (current_time - last_activity_time > 60000) { //idle for more than 60 secs
                idle_status = true;
            }
        }
    
        document.addEventListener('mousemove', resetIdleTime);
        document.addEventListener('keypress', resetIdleTime);
        document.addEventListener('click', resetIdleTime);
}

function detectResize(){
    let previousWidth = window.outerWidth;
    let previousHeight = outerHeight;

    function logResize(){      
        const currentWidth = window.outerWidth;
        const currentHeight = window.outerHeight;

        let action = "resized";
        if (currentWidth === screen.availWidth && currentHeight === screen.availHeight) {
            action = "maximized";
        } 
        else if (currentWidth < previousWidth && currentHeight < previousHeight) {
            action = "minimized or resized smaller";
        }

        uploadBrowserActivityLog(`Window ${action}`, 1);
    }

    window.addEventListener('resize', logResize);

}

function detectPageReload(){
    window.addEventListener('load', () => {
        if (performance.navigation.type === performance.navigation.TYPE_RELOAD) {
            console.log('Page was reloaded.');
            uploadBrowserActivityLog('Page reload', 0);
        }
    });
}

function detectDevTool(){
    let dev_tool_open = false;

    setInterval(function() {
        if (window.console && (console.firebug || console.table && console.dir)) {
            if (!dev_tool_open) {
                //DevTools is opened
                dev_tool_open = true;
                uploadBrowserActivityLog('Developer Tools is open', 2);
            }
        } else {
            if (dev_tool_open) {
                //DevTools is closed
                dev_tool_open = false; 
            }
        }
    }, 1000);
}

function detectWindowPosChange(){
    let previous_left = window.screenX;
    let previous_top = window.screenY;

    // Detect window movement
    setInterval(function() {
        const current_left = window.screenX;
        const current_top = window.screenY;

        if (current_left !== previous_left || current_top !== previous_top) {
            uploadBrowserActivityLog('Window moved to a different position, change screen possible', 1);
        }

        // Update the previous window position
        previous_left = current_left;
        previous_top = current_top;
    }, 1000);
}

function detectNetworkConnectionLost(){
    let connected_to_network = true;

    window.addEventListener('offline', function() {
        connected_to_network = false;
    });
    
    window.addEventListener('online', function() {
        if(!connected_to_network){
            uploadBrowserActivityLog("Network reconnected after network disconnection detected", 1);
            connected_to_network = true;
        }
    });
}

// Handles submit
function handleSubmit(event) {
    event.preventDefault();

    const userConfirmed = confirm("Are you sure you want to end this exam?");

    if(userConfirmed){
        sessionSaveSelectedAnswers();

        document.querySelector("form").submit();
    }
}
