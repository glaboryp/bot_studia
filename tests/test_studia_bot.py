import os
import sys
import unittest

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


if __name__ == '__main__':
    unittest.main()
