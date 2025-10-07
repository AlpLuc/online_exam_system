from django.test import TestCase
from .models import Faculty, Programme, Student, Lecturer, Course
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import datetime
from .tokens import account_activation_token
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.contrib.messages import get_messages

class FacultyModelTest(TestCase):
    def test_create_faculty(self):
        faculty = Faculty.objects.create(name="Engineering")
        self.assertEqual(faculty.name, "Engineering")
        self.assertEqual(str(faculty), "Engineering")


class ProgrammeModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(name="Engineering")

    def test_create_programme(self):
        programme = Programme.objects.create(faculty=self.faculty, name="Computer Science")
        self.assertEqual(programme.name, "Computer Science")
        self.assertEqual(programme.faculty, self.faculty)
        self.assertEqual(str(programme), "Computer Science")


class StudentModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(name="Engineering")
        self.programme = Programme.objects.create(faculty=self.faculty, name="Computer Science")
        self.user = User.objects.create_user(username="studentuser", password="password123", first_name="Studentuser", last_name="Studentuser")

    def test_create_student(self):
        student = Student.objects.create(
            user=self.user,
            programme=self.programme,
            cohort="2025",
            register_date=datetime.date(2021, 9, 1),
            phone_num="+1234567890",
        )
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.programme, self.programme)
        self.assertEqual(student.cohort, "2025")
        self.assertEqual(student.phone_num, "+1234567890")
        self.assertEqual(str(student), "Studentuser Studentuser".title())


class LecturerModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(name="Engineering")
        self.user = User.objects.create_user(username="lectureruser", password="password123", first_name="Lectureruser", last_name="Lectureruser")

    def test_create_lecturer(self):
        lecturer = Lecturer.objects.create(
            user=self.user,
            faculty=self.faculty,
            title="Dr.",
            phone_num="+9876543210",
        )
        self.assertEqual(lecturer.user, self.user)
        self.assertEqual(lecturer.faculty, self.faculty)
        self.assertEqual(lecturer.title, "Dr.")
        self.assertEqual(lecturer.phone_num, "+9876543210")
        self.assertEqual(str(lecturer), "Dr. Lectureruser Lectureruser".title())


class CourseModelTest(TestCase):
    def setUp(self):
        self.faculty = Faculty.objects.create(name="Engineering")
        self.programme = Programme.objects.create(faculty=self.faculty, name="Computer Science")
        self.lecturer = Lecturer.objects.create(
            user=User.objects.create_user(username="lectureruser", password="password123"),
            faculty=self.faculty,
            title="Dr.",
            phone_num="+9876543210",
        )

    def test_create_course(self):
        course = Course.objects.create(
            programme=self.programme,
            lecturer=self.lecturer,
            code="CS101",
            name="Introduction to Computer Science"
        )
        self.assertEqual(course.programme, self.programme)
        self.assertEqual(course.lecturer, self.lecturer)
        self.assertEqual(course.code, "CS101")
        self.assertEqual(course.name, "Introduction to Computer Science")
        self.assertEqual(str(course), "Introduction to Computer Science")

class LoginPageTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('user_login'), {'username': 'testuser', 'password': 'testpassword'})
        
        # Check if the user is redirected to the home page after login
        self.assertRedirects(response, reverse('home'))
        # Check if the user is logged in
        self.assertTrue(self.client.login(username='testuser', password='testpassword'))

    def test_login_failure(self):
        """Test failed login due to incorrect credentials"""
        response = self.client.post(reverse('user_login'), {'username': 'testuser', 'password': 'wrongpassword'})

        # Check if the user is redirected back to the login page
        self.assertRedirects(response, reverse('user_login'))

        # Check if the error message is displayed
        messages_list = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Incorrect username or password, Try Again")

    def test_login_page_get(self):
        """Test GET request to ensure the login page renders correctly"""
        response = self.client.get(reverse('user_login'))
        
        # Check if the login page is rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authenticate/login.html')

class LogoutPageTest(TestCase):
    def setUp(self):
        # Create a test user and log them in
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        self.logout_url = reverse('logout')  # Replace 'logout' with the name of your logout view in the URL patterns
        self.home_url = reverse('home')

    def test_logout_success(self):
        # Test user logout
        response = self.client.get(self.logout_url)
        # Assert user is logged out
        self.assertNotIn('_auth_user_id', self.client.session)
        # Assert redirection to home page
        self.assertRedirects(response, self.home_url)
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_logout_success(self):
        """Test user logout and redirection to home page"""
        # Log in the user first
        self.client.login(username='testuser', password='testpassword')

        # Send a POST request to log out
        response = self.client.get(reverse('logout'))  # Replace 'logout' with the actual name of your logout URL

        # Check if the user is redirected to the home page after logout
        self.assertRedirects(response, reverse('home'))

        # Check if the user is logged out (the session should not contain the user)
        response = self.client.get(reverse('home'))  # Get the home page after logout
        self.assertNotContains(response, 'testuser')  # Ensure the user is not logged in anymore
        
class ActivateViewTestCase(TestCase):
    def setUp(self):
        # Create an inactive test user
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            is_active=False
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)
        self.invalid_uid = urlsafe_base64_encode(force_bytes(999999))  # Invalid UID
        self.invalid_token = "invalid-token"
        self.activate_url = reverse('activate', kwargs={'uidb64': self.uid, 'token': self.token})

    def test_activate_success(self):
        # Test successful activation
        response = self.client.get(self.activate_url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertRedirects(response, reverse('user_login'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Thank you for your email confirmation. Now you can login your account.")

    def test_activate_invalid_uid(self):
        # Test activation with an invalid UID
        invalid_uid_url = reverse('activate', kwargs={'uidb64': self.invalid_uid, 'token': self.token})
        response = self.client.get(invalid_uid_url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertRedirects(response, reverse('user_login'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Activation link is invalid!")

    def test_activate_invalid_token(self):
        # Test activation with an invalid token
        invalid_token_url = reverse('activate', kwargs={'uidb64': self.uid, 'token': self.invalid_token})
        response = self.client.get(invalid_token_url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertRedirects(response, reverse('user_login'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Activation link is invalid!")