from django.db import models


# Create your models here.
class SavedColor(models.Model):
    MAX_PIN_VALUE = 255
    name = models.CharField(max_length=256, default='unnamed')
    red = models.PositiveSmallIntegerField(default=0)
    green = models.PositiveSmallIntegerField(default=0)
    blue = models.PositiveSmallIntegerField(default=0)
    brightness = models.PositiveSmallIntegerField(default=255)

    def get_red(self):
        # returns red multiplied by the brightness ratio
        return self.red * self.get_brightness()

    def get_green(self):
        # returns green multiplied by the brightness ratio
        return self.green * self.get_brightness()

    def get_blue(self):
        # returns blue multiplied by the brightness ratio
        return self.blue * self.get_brightness()

    def get_brightness(self):
        # returns brightness ratio
        return self.brightness/self.MAX_PIN_VALUE

    @staticmethod
    def validate_params(params):
        if SavedColor.is_in_range(params['red']) \
                and SavedColor.is_in_range(params['green']) \
                and SavedColor.is_in_range(params['blue']) \
                and SavedColor.is_in_range(params['brightness']):
            return True
        return False

    @staticmethod
    def is_in_range(value):
        return 0 <= value <= SavedColor.MAX_PIN_VALUE

    @staticmethod
    def get_default():
        result = SavedColor.objects.get_or_create(name='default', defaults={
            'red': 0,
            'green': 0,
            'blue': 0,
            'brightness': 255
        })
        return result[0]

    @staticmethod
    def is_name_valid(name):
        return name != 'default'

    @staticmethod
    def get_by_id(pk):
        color = None
        try:
            color = SavedColor.objects.get(pk=pk)
        except SavedColor.DoesNotExist:
            print('Error: SavedColor with id \''+pk+'\' does not exist.')
        return color


class CurrentColorState(models.Model):
    name = models.CharField(max_length=64)
    color = models.ForeignKey(SavedColor, on_delete=models.CASCADE, related_name='color')
    power = models.BooleanField(default=False)

    def toggle_power(self):
        self.power = not self.power
        self.save()

    def is_on(self):
        return self.power

    def set_color(self, new_color):
        self.color = new_color
        self.save()

    def set_color_to_default(self):
        self.set_color(SavedColor.get_default())

    @staticmethod
    def get_current_state():
        result = CurrentColorState.objects.get_or_create(name='default', defaults={
            'color': SavedColor.get_default()
        })
        return result[0]


class ScheduledColorChange(models.Model):
    # possible values for effect
    UPDATE = 'UC'
    TEMPORARY = 'TC'
    BREATHE = 'BE'
    EFFECT_CHOICES = (
        (UPDATE, 'Update Color'),
        (TEMPORARY, 'Temporarily Update Color'),
        (BREATHE, 'Breathe Effect'),
    )

    # possible values for state
    NOT_STARTED = 'NS'
    RUNNING = 'RN'
    COMPLETE = 'CP'
    STATE_CHOICES = (
        (NOT_STARTED, 'Not Started'),
        (RUNNING, 'Running'),
        (COMPLETE, 'Complete'),
    )

    # fields
    dateTime = models.DateTimeField()
    duration = models.DurationField()
    effect = models.CharField(max_length=2, choices=EFFECT_CHOICES, default=UPDATE)
    target = models.ForeignKey(SavedColor, on_delete=models.CASCADE, related_name='target')
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=NOT_STARTED)

    def is_past_sched_datetime(self):
        return False

    def is_within_duration(self):
        return False

    def is_duration_expired(self):
        return False

    def update_state(self):
        return

    def is_running(self):
        return False

    def is_not_started(self):
        return False

    def is_complete(self):
        return False

    def is_update(self):
        return False

    def is_temp(self):
        return False

    def is_breathe(self):
        return False
