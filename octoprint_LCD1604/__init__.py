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

        # init lcd

        self.cols = 20
        self.rows = 4

        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
                           cols=self.cols, rows=self.rows, dotsize=8,
                           charmap='A00',
                           auto_linebreaks=False,
                           backlight_enabled=True)

        # init vars
        self.start_date = 0
        self.block = bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
        self.block.append(255)

        # create block for progress bar
        self.lcd.create_char(1, self.block)

    def on_after_startup(self):
        lcd = self.lcd
        self._logger.info("plugin initialized !")

    def on_print_progress(self, storage, path, progress):
        lcd = self.lcd

        # reset lcd
        # lcd.clear()

        str_completed = 'Completed:'
        str_progress = str(str(progress) + '%')

        lcd.cursor_pos = (0, 0)
        lcd.write_string(str_completed)

        if len(str_progress) > 0:
            lcd.cursor_pos = (0, int(self.cols - len(str_progress)))
            lcd.write_string(str_progress)

        lcd.cursor_pos = (1, 0)
        lcd.write_string('ETA:')

        percent = int(progress / 5) + 1
        completed = '\x01' * percent
        
        lcd.cursor_pos = (3, 0)
        lcd.write_string(completed)

        if progress == 1:
            self.start_date = time.time()

        if progress > 1 and progress < 100:
            now = time.time()
            elapsed = now - self.start_date
            average = elapsed / (progress - 1)
            remaining = int((100 - progress) * average)
            remaining = str(datetime.timedelta(seconds=remaining))

            if len(remaining) > 0:
                lcd.cursor_pos = (1, int(self.cols - len(remaining)))
                lcd.write_string(remaining)

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
