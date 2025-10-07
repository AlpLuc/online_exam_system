# WEB-BASED ONLINE EXAMINATION SYSTEM WITH ACTIVITY TRACKING AND SCREEN CAPTURE

This repository contains the source code for the Final Year Project (FYP) thesis titled "WEB-BASED ONLINE EXAMINATION SYSTEM WITH ACTIVITY TRACKING AND SCREEN CAPTURE".

## Overview

The evolution of the education system, accelerated by the COVID-19 pandemic, led to a significant shift towards online examinations, offering benefits such as remote access, time efficiency, and immediate feedback. However, a major challenge identified in online exams is maintaining **integrity** due to the absence of physical proctoring, which compromises the fairness and validity of the examination process and increases instances of cheating.

This project addresses these issues by proposing the development of a web-based online examination system specifically enhanced with **activity tracking** and **screen capture** features. The aim is to uphold the credibility of qualifications and ensure a secure, reliable online environment for conducting examinations, thereby preventing online cheating.

The methodology followed the **Waterfall Model** of the Software Development Life Cycle (SDLC), encompassing planning, analysis, design, implementation, and testing phases.

## Project Objectives Achieved

The system successfully achieved the following objectives:

1.  **Design** a web-based online examination system with user-centered design principles.
2.  **Implement** activity tracking and screen capturing within the system by employing systematic approaches like **automated user action tracking** and **real-time screen capture**.
3.  **Evaluate and test** the system through unit testing, integration testing, and the System Usability Scale (SUS).

## Core Features and Modules

The project scope included the design and development of multiple modules aimed at enhancing the online examination experience and ensuring integrity:

| Module | Description | User Roles | CRUD Support |
| :--- | :--- | :--- | :--- |
| **Student Management** | Manages student profiles (registration, editing, viewing personal information). Lecturers can view/delete student info. | Student, Admin | CRUD |
| **Lecturer Management** | Allows lecturers to manage their own profiles (registration, editing, viewing). Admins can delete accounts. | Lecturer, Admin | CRUD |
| **Exam Management** | Handles examination administration, including creating, distributing, and scheduling exams. | Lecturer, Admin | CRUD |
| **Completed Exam Management** | Stores completed exams and answers. Allows lecturers to grade papers, view performance reports, and delete student papers. Students can view grades and comments. | Student, Lecturer, Admin | CRUD |
| **Question Bank Management** | Manages question banks (creation, storage, edit, delete) to aid lecturer efficiency. | Lecturer, Admin | CRUD |
| **Notification Management** | Manages system notifications, providing students and lecturers with reminders (upcoming exams), grades, and updates. | Student, Lecturer, Admin | CRUD |
| **Screen Capture** | Captures students' screens during exams; captured screens (videos) are accessible by lecturers and admins for review. | Lecturer, Admin | CRUD |
| **Activity Tracking** | Tracks student’s activity during exams, including time taken on questions, tab switching, and copy/paste actions. Activities are recorded in an activity log. | Lecturer, Admin | CRUD |
| **Admin Panel** | Provides administrators full control to manage Users, Faculty, Course, Programme, and Group records (CRUD), and send manual notifications. | Admin | CRUD |

## Anti-Cheating and Integrity Mechanisms

The system incorporates several features to maintain exam integrity:

*   **Customizable Monitoring:** Lecturers can configure tracking settings, including enabling/disabling screen capture, tab switch monitoring, and browser activity monitoring.
*   **Real-time Screen Capture:** Uses the MediaDevices interface (WebRTC) to prompt the user to capture the entire screen. Screen recordings are segmented (10-second chunks) and are only uploaded and stored when **unwanted behavior is detected**.
*   **Automated User Action Tracking (Browser Activity Log):** Monitors and logs suspicious activities, categorized by status level (0, 1, or 2), including:
    *   Detecting Tab Switch/Minimization (using `visibilityState`).
    *   Detecting Window Focus or Blur.
    *   Detecting Idle time (if no activity for > 60 seconds).
    *   Detecting Window Resize/Maximize/Minimize.
    *   Detecting Page Reloads.
    *   Detecting Developer Tool openings (via window console/firebug check).
    *   Detecting Window Position Changes.
    *   Detecting Network Connection Loss/Reconnect.
    *   Restricting Cut, Copy, and Paste.
    *   Preventing Browser Back actions.
*   **Secure Exam Environment:** Questions are hidden until the student initiates **Full Screen mode**.
*   **URL Encryption:** Sensitive IDs (like exam or user IDs) are encrypted in the URL using **Fernet symmetric encryption**. This scheme uses **AES-128 in CBC mode** for encryption and **HMAC with SHA-256** for authentication, preventing direct exposure and tampering of database IDs.
*   **Question Randomization:** Questions and options can be randomized if set in the exam configuration.

## Technology Stack

The system was implemented using the following technologies and libraries:

| Component | Technology | Role / Version |
| :--- | :--- | :--- |
| **Primary Language** | Python | 3.12.8 |
| **Backend Framework** | Django | 5.1 (following MVT architectural pattern) |
| **Database Management** | MySQL | Used for efficient data storage and retrieval |
| **Frontend Styling** | Bootstrap | 5.1 |
| **Frontend Scripting** | JavaScript, Custom CSS | Used for interactivity, real-time tracking, and dynamic UI elements |
| **Task Queue** | Celery Beat | Used for scheduling periodic tasks (e.g., exam reminders) |
| **Message Broker** | Redis | Configured as the message broker for communication between Django and Celery |
| **Reporting/Data Visualization** | Chart.js | Used for creating bar charts in exam reports |

## Author and Institution

*   **Author:** LUCAS TAN GUANG QUAN
*   **Degree:** Bachelor of Computer Science with Honours (Network Engineering)
*   **Institution:** Faculty of Computing and Informatics, Universiti Malaysia Sabah
*   **Year of Thesis Submission:** 2025
*   **Link to Thesis** https://docs.google.com/document/d/1JmjczEyRf1Z5tue9gdVnY8FpttUOq3KEau_5eEoPG6w/edit?usp=sharing
