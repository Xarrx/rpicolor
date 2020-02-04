from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import SavedColor
from .models import CurrentColorState
import json
import pigpio

RED_PIN = 17
GREEN_PIN = 22
BLUE_PIN = 24

pi = pigpio.pi()

# Create your views here.


def simulated_led_strip(request):
    return render(request, 'main/ledstrip.html')


class Manage(View):

    @staticmethod
    def helper(args):
        pass

    def get(self, request):
        args = request.GET
        return render(request, 'main/manage.html')

    def post(self, request):
        args = request.POST
        pass


class ColorAPI(View):

    # GET request options
    GETCOLOR = 'getColor'
    GETPOWERSTATE = 'getPowerState'
    GETCOLORS = 'getColors'

    GETSCHEDCOLORS = 'getSchedColors'

    # POST request options
    SETCOLOR = 'setColor'
    SAVECOLOR = 'saveColor'
    UPDATECOLOR = 'updateColor'
    TOGGLEPWRSTATE = 'togglePwrState'
    DELETECOLOR = 'deleteColor'

    SAVESCHEDCOLOR = 'saveSchedColor'
    UPDATESCHEDCOLOR = 'updateSchedColor'
    DELETESCHEDCOLOR = 'deleteSchedColor'

    # Errors
    NO_ACTION = 'No action string found in request.'
    BAD_ACTION = 'Invalid action string \'{0}\' received for method \'{1}\'.'  # 1st: received string; 2nd: method;

    NO_PARAMS = 'The action specified requires params but none were found in request.'
    BAD_PARAMS = 'Invalid params received for action \'{0}\'.'

    RESERVED_NAME_PARAM = 'Invalid name in params: name cannot be \'default\'.'
    LARGE_NAME_PARAM = 'Invalid name in params: name can be a max of 256 characters in length.'
    EMPTY_NAME_PARAM = 'Invalid name in params: name cannot be an empty string.'

    BAD_COLOR_PARAM = 'Invalid color value in params: one or more of the values (red, green, blue, brightness) is '\
                      'invalid. Color values must be unsigned integers in the range [0, 255].'
    BAD_ID_PARAM = 'Invalid id in params: a color with this id does not exist.'

    # Other messages
    UNDER_DEVELOPMENT = 'This action is currently under development.'

    @staticmethod
    def get_helper(args):
        # helper for the get function to allow easier testing
        response = ({}, 200)
        if 'action' in args:
            action = args['action']
            state = CurrentColorState.get_current_state()
            if action == ColorAPI.GETCOLOR:
                current_color = state.color
                response = ({
                    'color': {
                        'red': current_color.red,
                        'green': current_color.green,
                        'blue': current_color.blue,
                        'brightness': current_color.brightness
                    }
                }, 200)
            elif action == ColorAPI.GETPOWERSTATE:
                response = ({
                    'power': state.power
                }, 200)
            elif action == ColorAPI.GETCOLORS:
                def map_helper(x):
                    return {
                        'name': x.name,
                        'id': x.id,
                        'red': x.red,
                        'green': x.green,
                        'blue': x.blue,
                        'brightness': x.brightness,
                    }
                colors = list(map(map_helper, list(SavedColor.objects.all())))
                response = ({'colors': colors}, 200)
            elif action == ColorAPI.GETSCHEDCOLORS:
                response = ({
                    'message': ColorAPI.UNDER_DEVELOPMENT
                }, 200)
            else:
                response = ({
                    'message': ColorAPI.BAD_ACTION.format(action, 'GET')
                }, 500)
        else:
            response = ({
                'message': ColorAPI.NO_ACTION
            }, 500)

        return response

    @staticmethod
    def post_helper(args):
        # helper for the post function to allow easier testing
        response = ({}, 200)
        if 'action' in args:
            action = args['action']
            state = CurrentColorState.get_current_state()
            if action == ColorAPI.SETCOLOR:
                #
                # multiple ways this can proceed:
                # 1. change the default color to the color values given.
                # 2. change the color that the default state points to.
                #
                if 'params' in args:
                    params = json.loads(args['params'])
                    if 'red' in params \
                            and 'green' in params \
                            and 'blue' in params \
                            and 'brightness' in params:
                        #
                        #   1)  in this case, it is expected that there is a 'params' field in the request containing
                        #       new color values to be assigned to the default color.
                        #       {..., params: {red: 0, green: 0, blue: 255, brightness: 255}, ...}
                        #
                        try:
                            if SavedColor.validate_params(params):
                                default = SavedColor.get_default()
                                default.red = params['red']
                                default.green = params['green']
                                default.blue = params['blue']
                                default.brightness = params['brightness']
                                default.save()
                                state = CurrentColorState.get_current_state()
                                state.set_color_to_default()
                                response = ({'color': {
                                    'red': default.red,
                                    'green': default.green,
                                    'blue': default.blue,
                                    'brightness': default.brightness
                                }}, 200)
                                #
                                # pigpio call to update the pins would go here
                                #
                                pi = pigpio.pi()
                                red = (params['brightness']/255)*params['red']
                                green = (params['brightness']/255)*params['green']
                                blue = (params['brightness']/255)*params['blue']
                                pi.set_PWM_dutycycle(RED_PIN, red)
                                pi.set_PWM_dutycycle(GREEN_PIN, green)
                                pi.set_PWM_dutycycle(BLUE_PIN, blue)
                                pi.stop()
                            else:
                                #
                                # A param is out of range, respond with error.
                                #
                                response = ({
                                    'message': ColorAPI.BAD_COLOR_PARAM
                                }, 500)
                        except TypeError:
                            #
                            # A param is out of range, respond with error.
                            #
                            response = ({
                                'message': ColorAPI.BAD_COLOR_PARAM
                            }, 500)
                    elif 'id' in params:
                        #
                        #   2)  in this case, an id is expected to be specified in the 'params' which indicates the
                        #       saved color that should be assigned to the default color state.
                        #       {..., params: {id: some_id}, ...}
                        #
                        pass
                    else:
                        #
                        # Bad params, respond with error.
                        #
                        response = ({
                            'message': ColorAPI.BAD_PARAMS.format(ColorAPI.SETCOLOR)
                        }, 500)
                else:
                    #
                    # No params, respond with error.
                    #
                    response = ({
                        'message': ColorAPI.NO_PARAMS
                    }, 500)
            elif action == ColorAPI.SAVECOLOR:
                #
                # Expects params to contain the color information much like set color case 1 with the addition of a name
                # being specified. an error occurs if the name is 'default' as this name is reserved. additional errors
                # for names exceeding 256 characters and empty strings.
                #
                if 'params' in args:
                    params = json.loads(args['params'])
                    if 'name' in params and 'red' in params and 'green' in params and 'blue' in params \
                            and 'brightness' in params:
                        if SavedColor.validate_params(params) and SavedColor.is_name_valid(params['name']):
                            new = SavedColor(name=params['name'],
                                             red=params['red'],
                                             green=params['green'],
                                             blue=params['blue'],
                                             brightness=params['brightness'])
                            new.save()
                            response = ({'color': {
                                'name': new.name,
                                'id': new.id,
                                'red': new.red,
                                'green': new.green,
                                'blue': new.blue,
                                'brightness': new.brightness
                            }}, 200)
                        else:
                            #
                            # A param is out of range, respond with error.
                            #
                            response = ({
                                'message': ColorAPI.BAD_COLOR_PARAM
                            }, 500)
                    else:
                        #
                        # Bad params, respond with error.
                        #
                        response = ({
                            'message': ColorAPI.BAD_PARAMS.format(ColorAPI.SAVECOLOR)
                        }, 500)
                else:
                    #
                    # No params, respond with error.
                    #
                    response = ({
                        'message': ColorAPI.NO_PARAMS
                    }, 500)
            elif action == ColorAPI.UPDATECOLOR:
                #
                # Expects params to contain the color information (ie. red, green, blue, brightness) as well as the id
                # of the saved color to be updated. Errors if params is missing, colors out of range.
                #
                if 'params' in args:
                    params = json.loads(args['params'])
                    if 'id' in params and 'name' in params and 'red' in params and 'green' in params \
                            and 'blue' in params and 'brightness' in params:
                        try:
                            if SavedColor.validate_params(params) and SavedColor.is_name_valid(params['name']):
                                color = SavedColor.objects.get(pk=params['id'])
                                color.name = params['name']
                                color.red = params['red']
                                color.green = params['green']
                                color.blue = params['blue']
                                color.brightness = params['brightness']
                                color.save()
                                response = ({'color': {
                                    'name': color.name,
                                    'id': color.id,
                                    'red': color.red,
                                    'green': color.green,
                                    'blue': color.blue,
                                    'brightness': color.brightness
                                }}, 200)
                            else:
                                #
                                # A param is out of range, respond with error.
                                #
                                response = ({
                                                'message': ColorAPI.BAD_COLOR_PARAM
                                            }, 500)
                        except TypeError:
                            #
                            # A param is out of range, respond with error.
                            #
                            response = ({
                                'message': ColorAPI.BAD_COLOR_PARAM
                            }, 500)
                        except SavedColor.DoesNotExist:
                            #
                            # Bad id param, respond with error
                            #
                            response = ({
                                'message': ColorAPI.BAD_ID_PARAM
                            }, 500)
                    else:
                        #
                        # Bad params, respond with error.
                        #
                        response = ({
                            'message': ColorAPI.BAD_PARAMS.format(ColorAPI.UPDATECOLOR)
                        }, 500)
                else:
                    #
                    # No params, respond with error.
                    #
                    response = ({
                        'message': ColorAPI.NO_PARAMS
                    }, 500)
            elif action == ColorAPI.TOGGLEPWRSTATE:
                #
                # Expects no params. Toggles the 'LED strip' on and off. Responds with the new power state as 'power'.
                # No errors possible.
                #
                pi = pigpio.pi()
                state = CurrentColorState.get_current_state()
                state.toggle_power()
                response = ({'power': state.power}, 200)

                if state.power:
                    # on
                    default = SavedColor.get_default()
                    red = (default.brightness / 255) * default.red
                    green = (default.brightness / 255) * default.green
                    blue = (default.brightness / 255) * default.blue
                    pi.set_PWM_dutycycle(RED_PIN, red)
                    pi.set_PWM_dutycycle(GREEN_PIN, green)
                    pi.set_PWM_dutycycle(BLUE_PIN, blue)
                else:
                    # off
                    pi.set_PWM_dutycycle(RED_PIN, 0)
                    pi.set_PWM_dutycycle(GREEN_PIN, 0)
                    pi.set_PWM_dutycycle(BLUE_PIN, 0)

                pi.stop()
            elif action == ColorAPI.DELETECOLOR:
                #
                # Expects params to contain the id of the color to delete. Error if id is missing or invalid.
                #
                try:
                    params = json.loads(args['params'])
                    color = SavedColor.objects.get(pk=params['id']).delete()
                    response = ({'count': color[0]}, 200)
                except KeyError:
                    #
                    # Bad params, respond with error.
                    #
                    response = ({
                        'message': ColorAPI.BAD_PARAMS.format(ColorAPI.DELETECOLOR)
                    }, 500)
                except SavedColor.DoesNotExist:
                    #
                    # Bad id param, respond with error
                    #
                    response = ({
                        'message': ColorAPI.BAD_ID_PARAM
                    }, 500)
            else:
                response = ({
                    'message': ColorAPI.BAD_ACTION.format(action, 'GET')
                }, 500)
        else:
            response = ({
                'message': ColorAPI.NO_ACTION
            }, 500)

        return response

    def get(self, request):
        args = request.GET
        response = self.get_helper(args)
        return JsonResponse(response[0], status=response[1])

    def post(self, request):
        args = request.POST
        response = self.post_helper(args)
        return JsonResponse(response[0], status=response[1])
