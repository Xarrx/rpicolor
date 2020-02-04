import datetime
import ast
from django.test import TestCase
from django.utils import timezone
from .models import SavedColor
from .models import CurrentColorState
from .models import ScheduledColorChange
from .views import ColorAPI


# Create your tests here.


class SavedColorModelTests(TestCase):

    def test_get_brightness_calculates_ratio(self):
        color = SavedColor(name='testName', red=255, green=255, blue=255, brightness=0)
        for i in range(255):
            color.brightness = i
            self.assertAlmostEqual(i/255, color.get_brightness())

    def test_get_red_adjusts_value_for_brightness(self):
        color = SavedColor(name='testName', red=255, green=255, blue=255, brightness=0)
        for i in range(255):
            color.red = i
            for j in range(255):
                color.brightness = j
                self.assertAlmostEqual(i*(j/255), color.get_red())

    def test_get_green_adjusts_value_for_brightness(self):
        color = SavedColor(name='testName', red=255, green=255, blue=255, brightness=0)
        for i in range(255):
            color.green = i
            for j in range(255):
                color.brightness = j
                self.assertAlmostEqual(i*(j/255), color.get_green())

    def test_get_blue_adjusts_value_for_brightness(self):
        color = SavedColor(name='testName', red=255, green=255, blue=255, brightness=0)
        for i in range(255):
            color.blue = i
            for j in range(255):
                color.brightness = j
                self.assertAlmostEqual(i*(j/255), color.get_blue())


class CurrentColorStateTests(TestCase):

    def test_toggle_power(self):
        state = CurrentColorState(name='testName')
        self.assertFalse(state.power)
        state.toggle_power()
        self.assertTrue(state.power)
        state.toggle_power()
        self.assertFalse(state.power)
        state.toggle_power()
        self.assertTrue(state.power)

    def test_is_on(self):
        state = CurrentColorState(name='testName')
        self.assertFalse(state.is_on())
        state.toggle_power()
        self.assertTrue(state.is_on())


class ScheduledColorChangeTests(TestCase):

    def test_is_past_sched_datetime(self):
        self.fail()

    def test_is_within_duration(self):
        self.fail()

    def test_is_duration_expired(self):
        self.fail()

    def test_update_state(self):
        self.fail()

    def test_is_running(self):
        self.fail()

    def test_is_not_started(self):
        self.fail()

    def test_is_complete(self):
        self.fail()

    def test_is_update(self):
        self.fail()

    def test_is_temp(self):
        self.fail()

    def test_is_breathe(self):
        self.fail()


class ColorAPITests(TestCase):

    #
    # general get helper tests
    #
    def test_get_helper_responds_with_error_with_no_action(self):
        response = ColorAPI.get_helper({})
        exp = ({"message": "No action string found in request."}, 500)
        self.assertTrue(response == exp)

    def test_get_helper_responds_with_error_with_invalid_action(self):
        response = ColorAPI.get_helper({'action': 'ashdfkjshdflkj'})
        exp = ({"message": "Invalid action string 'ashdfkjshdflkj' received for method 'GET'."}, 500)
        self.assertTrue(response == exp)

    #
    # get color tests
    #
    def test_get_helper_responds_with_color_on_valid_setup(self):
        # SavedColor.get_default()
        response = ColorAPI.get_helper({'action': 'getColor'})
        exp = ({"color": {"red": 0, "green": 0, "blue": 0, "brightness": 255}}, 200)
        self.assertTrue(response == exp)

    def test_get_helper_responds_with_power_state_on_valid_setup(self):
        # SavedColor.get_default()
        CurrentColorState.get_current_state()
        response = ColorAPI.get_helper({'action': 'getPowerState'})
        exp = ({"power": False}, 200)
        self.assertTrue(response == exp)

    def test_get_helper_responds_with_color_list_on_valid_setup(self):
        # set up some data
        default = SavedColor.get_default()
        color1 = SavedColor(name='color1')
        color1.save()
        color2 = SavedColor(name='color2')
        color2.save()
        color3 = SavedColor(name='color3')
        color3.save()
        response = ColorAPI.get_helper({'action': 'getColors'})
        exp = ({"colors": [
            {
                "name": "default",
                "id": default.id,
                "red": 0,
                "green": 0,
                "blue": 0,
                "brightness": 255,
            },
            {
                "name": "color1",
                "id": color1.id,
                "red": 0,
                "green": 0,
                "blue": 0,
                "brightness": 255,
            },
            {
                "name": "color2",
                "id": color2.id,
                "red": 0,
                "green": 0,
                "blue": 0,
                "brightness": 255,
            },
            {
                "name": "color3",
                "id": color3.id,
                "red": 0,
                "green": 0,
                "blue": 0,
                "brightness": 255,
            }
        ]}, 200)
        print(response[0])
        self.assertTrue(response == exp)

    #
    # general post helper tests
    #
    def test_post_helper_responds_with_error_with_no_action(self):
        response = ColorAPI.post_helper({})
        exp = ({"message": "No action string found in request."}, 500)
        self.assertTrue(response == exp)

    def test_post_helper_responds_with_error_with_invalid_action(self):
        response = ColorAPI.post_helper({'action': 'ashdfkjshdflkj'})
        exp = ({"message": "Invalid action string 'ashdfkjshdflkj' received for method 'GET'."}, 500)
        self.assertTrue(response == exp)

    #
    # set color tests
    #
    def test_post_helper_responds_with_error_on_set_color_with_no_params(self):
        response = ColorAPI.post_helper({'action': 'setColor'})
        exp = ({"message": "The action specified requires params but none were found in request."}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_0(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 256,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_1(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': -1,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_2(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 0,
            'green': 256,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_3(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 0,
            'green': -1,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_4(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 0,
            'green': 0,
            'blue': 256,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_5(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 0,
            'green': 0,
            'blue': -1,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_6(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': 256
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_set_color_with_bad_color_params_7(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': -1
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_helper_responds_with_error_on_set_color_with_missing_params(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 0,
            'g': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({"message": ColorAPI.BAD_PARAMS.format(ColorAPI.SETCOLOR)}, 500)
        self.assertTrue(response == exp)

    def test_post_helper_response_with_success_on_set_color_with_valid_params(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'red': 25,
            'green': 0,
            'blue': 255,
            'brightness': 255
        }})
        exp = ({'color': {
            'red': 25,
            'green': 0,
            'blue': 255,
            'brightness': 255
        }}, 200)
        self.assertTrue(response == exp)

    #
    # save color tests
    #
    def test_post_helper_responds_with_error_on_save_color_with_no_params(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR})
        exp = ({"message": "The action specified requires params but none were found in request."}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_0(self):
        response = ColorAPI.post_helper({'action': 'setColor', 'params': {
            'name': 'asdf',
            'red': 256,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_1(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': -1,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_2(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 0,
            'green': 256,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_3(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 0,
            'green': -1,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_4(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': 256,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_5(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': -1,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_6(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': 256
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_7(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': -1
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_save_color_with_bad_color_params_8(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'default',
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_helper_responds_with_error_on_save_color_with_missing_params(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 0,
            'g': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({"message": ColorAPI.BAD_PARAMS.format(ColorAPI.SAVECOLOR)}, 500)
        self.assertTrue(response == exp)

    def test_post_helper_response_with_success_on_save_color_with_valid_params(self):
        response = ColorAPI.post_helper({'action': ColorAPI.SAVECOLOR, 'params': {
            'name': 'asdf',
            'red': 25,
            'green': 0,
            'blue': 255,
            'brightness': 255
        }})
        exp = {
            'name': 'asdf',
            'red': 25,
            'green': 0,
            'blue': 255,
            'brightness': 255
        }
        status = 200
        self.assertTrue('color' in response[0])
        color = response[0]['color']
        self.assertTrue('red' in color
                        and 'green' in color
                        and 'blue' in color
                        and 'brightness' in color
                        and 'name' in color
                        and 'id' in color)
        self.assertEqual(exp['name'], color['name'])
        self.assertEqual(exp['red'], color['red'])
        self.assertEqual(exp['green'], color['green'])
        self.assertEqual(exp['blue'], color['blue'])
        self.assertEqual(exp['brightness'], color['brightness'])

    #
    # update color tests
    #
    def test_post_helper_responds_with_error_on_update_color_with_no_params(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR})
        exp = ({"message": "The action specified requires params but none were found in request."}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_0(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': 256,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_1(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': -1,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_2(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': 0,
            'green': 256,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_3(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': 0,
            'green': -1,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_4(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': 256,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_5(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': -1,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_6(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': 256
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_7(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': -1
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_8(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': 0,
            'name': 'default',
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_COLOR_PARAM}, 500)
        self.assertTrue(response == exp)

    def test_post_handler_responds_with_error_on_update_color_with_bad_color_params_9(self):
        response = ColorAPI.post_helper({'action': ColorAPI.UPDATECOLOR, 'params': {
            'id': -1,
            'name': 'asdf',
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': 255
        }})
        exp = ({'message': ColorAPI.BAD_ID_PARAM}, 500)
        self.assertTrue(response == exp)
