import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from studia_bot_definitivo import StudiaBotDefinitivo


def make_curso(nombre, capacidad=10, ocupacion=5, lugares=('Las Palmas',)):
    return {
        'nombre': nombre,
        'grupo_seleccionado': {'capacidad': capacidad, 'ocupacion': ocupacion},
        'grupos': [{'lugar': lugar} for lugar in lugares],
    }


class ExtractCoursesFromJsonTests(unittest.TestCase):
    def setUp(self):
        self.bot = StudiaBotDefinitivo()
        self.year = self.bot.target_year

    def test_includes_course_matching_month_year_and_valid_lugar(self):
        curso = make_curso(f'Curso anual estudios n - Julio {self.year}')

        courses = self.bot.extract_courses_from_json([curso])

        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]['month'], 'julio')
        self.assertEqual(courses[0]['plazas_disponibles'], 5)

    def test_excludes_semestre_courses(self):
        curso = make_curso(f'Curso Semestre Julio {self.year}')

        courses = self.bot.extract_courses_from_json([curso])

        self.assertEqual(courses, [])

    def test_excludes_course_with_empty_lugar_and_no_tafira_exception(self):
        curso = make_curso(f'Curso Julio {self.year}', lugares=('',))

        courses = self.bot.extract_courses_from_json([curso])

        self.assertEqual(courses, [])

    def test_includes_tafira_course_despite_empty_lugar(self):
        curso = make_curso(f'Residencia Tafira Atlantic Club Julio {self.year}', lugares=('',))

        courses = self.bot.extract_courses_from_json([curso])

        self.assertEqual(len(courses), 1)

    def test_excludes_course_without_available_plazas(self):
        curso = make_curso(f'Curso Julio {self.year}', capacidad=10, ocupacion=10)

        courses = self.bot.extract_courses_from_json([curso])

        self.assertEqual(courses, [])

    def test_handles_null_lugar_without_raising(self):
        curso = make_curso(f'Curso Julio {self.year}')
        curso['grupos'] = [{'lugar': None}]

        courses = self.bot.extract_courses_from_json([curso])

        self.assertEqual(courses, [])

    def test_excludes_course_outside_target_months(self):
        curso = make_curso(f'Curso Marzo {self.year}')

        courses = self.bot.extract_courses_from_json([curso])

        self.assertEqual(courses, [])


class TargetYearTests(unittest.TestCase):
    def test_target_years_includes_current_and_previous_year(self):
        bot = StudiaBotDefinitivo()

        current_year = int(bot.target_year)
        self.assertIn(str(current_year), bot.target_years)
        self.assertIn(str(current_year - 1), bot.target_years)


class LoginOriginTests(unittest.TestCase):
    def test_rejects_cross_origin_login_action_without_posting_credentials(self):
        bot = StudiaBotDefinitivo()
        login_page = MagicMock()
        login_page.text = (
            '<form action="https://evil.example/login">'
            '<input name="username"><input type="password" name="password"></form>'
        )
        login_page.raise_for_status.return_value = None
        bot.session.get = MagicMock(return_value=login_page)
        bot.session.post = MagicMock()

        self.assertFalse(bot.login())

        bot.session.post.assert_not_called()

    def test_rejects_insecure_login_action_on_the_same_host(self):
        bot = StudiaBotDefinitivo()
        login_page = MagicMock()
        login_page.text = (
            '<form action="http://studiaonline.org/login">'
            '<input name="username"><input type="password" name="password"></form>'
        )
        login_page.raise_for_status.return_value = None
        bot.session.get = MagicMock(return_value=login_page)
        bot.session.post = MagicMock()

        self.assertFalse(bot.login())

        bot.session.post.assert_not_called()

    def test_resolves_relative_login_action_on_the_configured_origin(self):
        bot = StudiaBotDefinitivo()
        bot.base_url = 'https://studiaonline.org/'
        login_page = MagicMock()
        login_page.text = (
            '<form action="/login">'
            '<input name="username"><input type="password" name="password"></form>'
        )
        login_page.raise_for_status.return_value = None
        logged_in = MagicMock()
        logged_in.text = '<main>ok</main>'
        logged_in.status_code = 200
        logged_in.raise_for_status.return_value = None
        bot.session.get = MagicMock(return_value=login_page)
        bot.session.post = MagicMock(return_value=logged_in)

        self.assertTrue(bot.login())

        self.assertEqual(bot.session.post.call_args.args[0], 'https://studiaonline.org/login')
        self.assertFalse(bot.session.post.call_args.kwargs['allow_redirects'])


class SearchFailureTests(unittest.TestCase):
    def test_does_not_overwrite_or_commit_state_when_course_fetch_fails(self):
        bot = StudiaBotDefinitivo()
        bot.get_available_courses = MagicMock(return_value=None)
        bot.load_previous_state = MagicMock(return_value={'existing': {}})
        bot.save_courses_state = MagicMock()
        bot.commit_state_changes = MagicMock()

        self.assertFalse(bot.run_search())

        bot.save_courses_state.assert_not_called()
        bot.commit_state_changes.assert_not_called()


if __name__ == '__main__':
    unittest.main()
