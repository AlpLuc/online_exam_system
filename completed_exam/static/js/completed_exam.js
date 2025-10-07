function switchQuestion(new_ques, ques_type){
    change = false;
    if(curr_ques_type != ques_type){
        document.getElementById(`${curr_ques_type}_question_btn${curr_ques}`).classList.remove('btn-primary');
        document.getElementById(`${curr_ques_type}_question_btn${curr_ques}`).classList.add('btn-light');
        document.getElementById(`${curr_ques_type}_question${curr_ques}`).style.display = "none";
        curr_ques_type = ques_type;
        change = true;            
    }

    if(ques_type == 'mcq'){
        if(!change){
            document.getElementById(`mcq_question_btn${curr_ques}`).classList.remove('btn-primary');
            document.getElementById(`mcq_question_btn${curr_ques}`).classList.add('btn-light');
            document.getElementById(`mcq_question${curr_ques}`).style.display = "none";
        }

        document.getElementById(`mcq_question_btn${new_ques}`).classList.remove('btn-light');
        document.getElementById(`mcq_question_btn${new_ques}`).classList.add('btn-primary');
        document.getElementById(`mcq_question${new_ques}`).style.display = "block";

        curr_ques = new_ques;
    }
    else if (ques_type == 'tf'){
        if(!change){
            document.getElementById(`tf_question_btn${curr_ques}`).classList.remove('btn-primary');
            document.getElementById(`tf_question_btn${curr_ques}`).classList.add('btn-light');
            document.getElementById(`tf_question${curr_ques}`).style.display = "none";
        }

        document.getElementById(`tf_question_btn${new_ques}`).classList.remove('btn-light');
        document.getElementById(`tf_question_btn${new_ques}`).classList.add('btn-primary');
        document.getElementById(`tf_question${new_ques}`).style.display = "block";

        curr_ques = new_ques;
    }
    else if (ques_type == 'essay'){   
        if(!change){     
            document.getElementById(`essay_question_btn${curr_ques}`).classList.remove('btn-primary');
            document.getElementById(`essay_question_btn${curr_ques}`).classList.add('btn-light');
            document.getElementById(`essay_question${curr_ques}`).style.display = "none";
        }
        document.getElementById(`essay_question_btn${new_ques}`).classList.remove('btn-light');
        document.getElementById(`essay_question_btn${new_ques}`).classList.add('btn-primary');
        document.getElementById(`essay_question${new_ques}`).style.display = "block";

        curr_ques = new_ques;
    }
    else{
        return;
    }
}

function validateDateTime() {
    const start_date_time = document.getElementById("id_start_date_time").value;
    const end_date_time = document.getElementById("id_end_date_time").value;

    console.log(start_date_time);
    console.log(end_date_time);

    if (new Date(end_date_time) < new Date(start_date_time)) {
        event.preventDefault();
        // Trigger popover for the end date time field
        const popoverField = document.getElementById("id_start_date_time");
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

function displayChart(values_list, element_id, chart_type, colour, data_label){
    // Get data from Django
    const values = values_list;  // Values as data
    const labels = Array.from({ length: values.length }, (_, i) => `Question ${i + 1}`);

    // Create the bar chart
    const ctx = document.getElementById(element_id).getContext('2d');
    new Chart(ctx, {
        type: chart_type,  // Chart type
        data: {
            labels: labels,  // X-axis labels
            datasets: [{
                label: data_label,
                data: values,  // Y-axis data
                backgroundColor: colour,
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

async function generatePDF(student_pages){
    const { jsPDF } = window.jspdf;

    const pdf = new jsPDF();
    const pageHeight = pdf.internal.pageSize.height;

    // Get content elements
    const general_content = document.getElementById('general_content');
    const chart_content = document.getElementById('chart_content');

    let currentY = 10; // Initial Y position

    // Render general_content and chart_content on page 1
    currentY = await renderContentToPDF(general_content, pdf, 10, currentY);

    //pdf.addPage();
    currentY = await renderContentToPDF(chart_content, pdf, 10, currentY-5);

    // Add a new page for student_content
    for (let i = 1; i <= student_pages; i++) {
        const student_content = document.getElementById('student_content' + i);

        pdf.addPage();
        await renderContentToPDF(student_content, pdf, 10, 10, true, pageHeight);
    } 
   
    // Save the PDF
    pdf.save('exam_report.pdf');

    async function renderContentToPDF(content, pdf, x, y, allowPagination = false, pageHeight = 0) {
        const canvas = await html2canvas(content);
        const imgData = canvas.toDataURL('image/png');
        const imgWidth = pdf.internal.pageSize.width - 20; // Account for margins
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        if (allowPagination) {
            let remainingHeight = imgHeight;
            while (remainingHeight > pageHeight - y - 10) {
                pdf.addImage(imgData, 'PNG', x, y, imgWidth, pageHeight - y - 10);
                pdf.addPage();
                remainingHeight -= pageHeight - 10;
                y = 10; // Reset Y for the new page
            }
            pdf.addImage(imgData, 'PNG', x, y, imgWidth, remainingHeight);
        } else {
            pdf.addImage(imgData, 'PNG', x, y, imgWidth, imgHeight);
            y += imgHeight + 10; // Update Y position for subsequent content
        }

        return y;
    }
}

function showLog(){
    document.getElementById("log_div").style.display = "block";
    document.getElementById("screen_capture_div").style.display = "none";
}

function showScreenCapture(){
    document.getElementById("screen_capture_div").style.display = "block";
    document.getElementById("log_div").style.display = "none";
}