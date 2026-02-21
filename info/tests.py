from django.test import TestCase
from django.urls import reverse
from django.test.client import Client

from info.models import (
    Dept,
    Class,
    Course,
    User,
    Student,
    Teacher,
    Assign,
    AssignTime,
    AttendanceTotal,
    Attendance,
    StudentCourse,
    Marks,
    MarksClass,
    AttendanceClass,
)


class InfoTest(TestCase):

    # ---------- helpers ----------

    def create_user(self, username='testuser', password='project123'):
        # Use create_user so passwords work for login
        return User.objects.create_user(username=username, password=password)

    def create_dept(self, id='CS', name='CS'):
        return Dept.objects.create(id=id, name=name)

    def create_class(self, id='CS5A', sem=5, section='A'):
        dept = self.create_dept()
        return Class.objects.create(id=id, dept=dept, sem=sem, section=section)

    def create_course(self, id='CS510', name='Data Struct', shortname='DS'):
        dept = self.create_dept(id='CS2')
        return Course.objects.create(id=id, dept=dept, name=name, shortname=shortname)

    def create_student(self, usn='CS01', name='samarth'):
        cl = self.create_class()
        u = self.create_user()
        return Student.objects.create(user=u, class_id=cl, USN=usn, name=name)

    def create_teacher(self, id='CS01', name='teacher'):
        dept = self.create_dept(id='CS3')
        return Teacher.objects.create(id=id, name=name, dept=dept)

    def create_assign(self, cl=None, cr=None, t=None):
        if cl is None:
            cl = self.create_class()
        if cr is None:
            cr = self.create_course()
        if t is None:
            t = self.create_teacher()
        return Assign.objects.create(class_id=cl, course=cr, teacher=t)

    # ---------- model tests ----------

    def test_user_creation(self):
        us = self.create_user()
        ut = self.create_user(username='teacher')
        # attach valid class / dept to avoid signals hitting missing FKs
        dept = self.create_dept(id='CS_MAIN', name='CS_MAIN')
        cl = Class.objects.create(id='CS_MAIN_5A', dept=dept, sem=5, section='A')
        s = Student(user=us, USN='CS01', name='test', class_id=cl)
        s.save()
        t = Teacher(user=ut, id='CS01', name='test', dept=dept)
        t.save()
        self.assertTrue(isinstance(us, User))
        self.assertEqual(us.is_student, hasattr(us, 'student'))
        self.assertEqual(ut.is_teacher, hasattr(ut, 'teacher'))

    def test_dept_creation(self):
        d = self.create_dept()
        self.assertTrue(isinstance(d, Dept))
        self.assertEqual(str(d), d.name)

    def test_class_creation(self):
        c = self.create_class()
        self.assertTrue(isinstance(c, Class))
        self.assertEqual(str(c), "%s : %d %s" % (c.dept.name, c.sem, c.section))

    def test_course_creation(self):
        c = self.create_course()
        self.assertTrue(isinstance(c, Course))
        self.assertEqual(str(c), c.name)

    def test_student_creation(self):
        s = self.create_student()
        self.assertTrue(isinstance(s, Student))
        self.assertEqual(str(s), s.name)

    def test_teacher_creation(self):
        t = self.create_teacher()
        self.assertTrue(isinstance(t, Teacher))
        self.assertEqual(str(t), t.name)

    def test_assign_creation(self):
        a = self.create_assign()
        self.assertTrue(isinstance(a, Assign))

    # ---------- view tests ----------

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test_user', 'test@test.com', 'test_password')

    def test_index_admin(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('index'))
        self.assertContains(response, "you have been logged out")
        self.assertEqual(response.status_code, 200)

    def test_index_student(self):
        self.client.login(username='test_user', password='test_password')
        dept = self.create_dept(id='CS4', name='CS4')
        cl = Class.objects.create(id='CS4A', dept=dept, sem=4, section='A')
        s = Student.objects.create(user=User.objects.first(), USN='test', name='test_name', class_id=cl)
        response = self.client.get(reverse('index'))
        self.assertContains(response, s.name)
        self.assertEqual(response.status_code, 200)

    def test_index_teacher(self):
        self.client.login(username='test_user', password='test_password')
        dept = self.create_dept(id='CS5', name='CS5')
        t = Teacher.objects.create(user=User.objects.first(), id='test', name='test_name', dept=dept)
        response = self.client.get(reverse('index'))
        self.assertContains(response, t.name)
        self.assertEqual(response.status_code, 200)

    def test_no_attendance(self):
        s = self.create_student()
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(reverse('attendance', args=(s.USN,)))
        self.assertContains(response, "student has no courses")
        self.assertEqual(response.status_code, 200)

    def test_attendance_view(self):
        s = self.create_student()
        self.client.login(username='test_user', password='test_password')
        # this creates Assign -> StudentCourse -> AttendanceTotal via signals
        self.create_assign(cl=s.class_id)
        response = self.client.get(reverse('attendance', args=(s.USN,)))
        self.assertEqual(response.status_code, 200)
        # AttendanceTotal has default __str__: "AttendanceTotal object (1)"
        self.assertQuerySetEqual(
            response.context['att_list'],
            ['AttendanceTotal object (1)'],
            transform=str,
        )

    def test_no_attendance__detail(self):
        s = self.create_student()
        cr = self.create_course()
        self.client.login(username='test_user', password='test_password')
        resp = self.client.get(reverse('attendance_detail', args=(s.USN, cr.id)))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "student has no attendance")

    def test_attendance__detail(self):
        s = self.create_student()
        cr = self.create_course()
        # create a valid Assign and AttendanceClass, and link Attendance to it
        assign = self.create_assign(cl=s.class_id, cr=cr)
        att_cls = AttendanceClass.objects.create(assign=assign, date='2018-10-23')
        Attendance.objects.create(student=s, course=cr, attendanceclass=att_cls)
        self.client.login(username='test_user', password='test_password')
        resp = self.client.get(reverse('attendance_detail', args=(s.USN, cr.id)))
        self.assertEqual(resp.status_code, 200)
        # Attendance.__str__ returns "student_name : course_shortname"
        self.assertQuerySetEqual(
            resp.context['att_list'],
            ['samarth : DS'],
            transform=str,
        )

