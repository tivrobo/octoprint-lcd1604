# coding=utf-8
from __future__ import absolute_import
from octoprint.printer.estimation import PrintTimeEstimator
import octoprint.plugin
import octoprint.events
from RPLCD.i2c import CharLCD
import time
import datetime


class OctoPrintLcd1604(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.EventHandlerPlugin,
                       octoprint.plugin.ProgressPlugin):

    def __init__(self):

        # init vars
        self.start_date = 0

        self.block = bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
        self.block.append(255)

        self.cols = 20
        self.rows = 4

        # init lcd
        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
                           cols=self.cols, rows=self.rows, dotsize=8,
                           charmap='A00',
                           auto_linebreaks=True,
                           backlight_enabled=True)

        # create block for progress bar
        self.lcd.create_char(1, self.block)

    def on_after_startup(self):
        lcd = self.lcd
        lcd.clear()
        self._logger.info("plugin initialized!")


    def on_print_progress(self, storage, path, progress):
        
        lcd = self.lcd
        lcd.clear()

        cols = self.cols
        rows = self.rows

        if progress == 0:
            self.start_date = time.time()
            self.start_time = time.strftime("%H:%M:%S")

        # progress
        str_progress = str(str(progress)+'%')

        lcd.cursor_pos = (0, 0)
        lcd.write_string('Progress:')

        lcd.cursor_pos = (0, int(cols - len(str_progress)))
        lcd.write_string(str_progress)

        # duration
        duration = int(time.time() - self.start_date)
        duration = str(datetime.timedelta(seconds=duration))

        lcd.cursor_pos = (1, 0)
        lcd.write_string('Duration:')

        lcd.cursor_pos = (1, int(cols - len(duration)))
        lcd.write_string(duration)

        # estimate
        lcd.cursor_pos = (2, 0)
        lcd.write_string('Estimate:')

        if progress > 5 and progress < 100:
            elapsed = time.time() - self.start_date
            average = elapsed / (progress - 1)
            remaining = int((100 - progress) * average)
            remaining = str(datetime.timedelta(seconds=remaining))
        else:
            remaining = str(datetime.timedelta(seconds=0))

        lcd.cursor_pos = (2, int(cols - len(remaining)))
        lcd.write_string(remaining)

        # progress bar
        percent = int(progress / (101 / cols))
        completed = '\x01' * percent

        lcd.cursor_pos = (3, 0)
        lcd.write_string(completed)

    def get_update_information(self):
        return dict(
            OctoPrintLcd1604=dict(
                displayName="OctoPrint LCD1604",
                displayVersion=self._plugin_version,
                type="github_release",
                current=self._plugin_version,
                user="tivrobo",
                repo="octoprint-lcd1604",
                pip="https://github.com/tivrobo/octoprint-lcd1604/archive/{target}.zip"
            )
        )


__plugin_name__ = "OctoPrint LCD1604"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OctoPrintLcd1604()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
