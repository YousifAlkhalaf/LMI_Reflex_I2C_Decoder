##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2012-2014 Uwe Hermann <uwe@hermann-uwe.de>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd
from enum import Enum


class Chip(Enum):
    PIC = 'PIC'
    BMS = 'BMS'
    HALL_EFFECT = 'Hall'
    USB_PD_IC = 'USB-PD-IC'


PIC = Chip.PIC
USB = Chip.USB_PD_IC
HALL = Chip.HALL_EFFECT
BMS = Chip.BMS

CHIP_MAP = {0x50: PIC, 0x28: USB, 0x5E: HALL, 0x0B: BMS}


class Decoder(srd.Decoder):
    api_version = 3
    id = 'lmi_reflex'
    name = 'LMI_Reflex'
    longname = 'LMI Reflex'
    desc = 'I2C decoder for LMI Reflex'
    license = 'gplv2+'
    inputs = ['i2c']
    outputs = []
    tags = ['LMI']
    options = (
        {'id': 'PIC', 'desc': 'Display PIC traffic', 'default': 'yes',
         'values': ('yes', 'no')},
        {'id': 'BMS', 'desc': 'Display BMS traffic', 'default': 'yes',
         'values': ('yes', 'no')},
        {'id': 'USB-PD-IC', 'desc': 'Display USB PD IC traffic', 'default': 'yes',
         'values': ('yes', 'no')},
        {'id': 'Hall', 'desc': 'Display Hall sensor traffic', 'default': 'yes',
         'values': ('yes', 'no')},
    )
    annotations = (
        ('chip-info', 'Chip Info'),  # 0
        ('pic_volt', 'Voltage'),  # 1
        ('pic_temp', 'Temperature'),  # 2
        ('pic_firm', 'Firmware'),  # 3
        ('pic_lumens', 'Lumens'),  # 4
        ('pic_fan', 'PWM fan'),  # 5
        ('pic_burst_stops', 'Burst(stops)'),  # 6
        ('pic_led', 'LED'),  # 7
        ('pic_flags', 'Flags'),  # 8
        ('pic_burst_pwm', 'Burst PWM'),  # 9
        ('pic_burst_delay', 'Burst Delay'),  # 10
        ('debug', 'Debug'),
    )
    annotation_rows = (
        ('chips', 'Chip info', (0,)),
        ('pic', 'PIC chip', (1, 2, 3, 4, 6, 7, 8, 9, 10)),
        ('debug_line', 'Debugging', (11,))
    )

    curr_chip = None
    is_writing = False
    shown_chips = []
    data_key = 0
    ann_start_pos = 0
    work_var = None  # Holds any var needed across samples

    out_ann = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.ann_start_pos = 0

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

        if self.options['PIC'] == 'yes':
            self.shown_chips.append(PIC)
        elif PIC in self.shown_chips:
            self.shown_chips.remove(PIC)
        if self.options['BMS'] == 'yes':
            self.shown_chips.append(BMS)
        elif BMS in self.shown_chips:
            self.shown_chips.remove(BMS)
        if self.options['Hall'] == 'yes':
            self.shown_chips.append(HALL)
        elif HALL in self.shown_chips:
            self.shown_chips.remove(HALL)
        if self.options['USB-PD-IC'] == 'yes':
            self.shown_chips.append(USB)
        elif USB in self.shown_chips:
            self.shown_chips.remove(USB)

    def put_ann(self, ssample, esample, data):
        self.put(ssample, esample, self.out_ann, data)

    def show_curr_chip(self):
        return self.curr_chip in self.shown_chips

    def get_data_ann(self, databyte):
        data = []
        if self.is_writing:
            pass
        else:
            if self.curr_chip == PIC:
                if self.data_key == 0:
                    voltage = int(databyte) / 10
                    data = [1,
                            ['Voltage: {}V'.format(voltage), 'Volts: {}V'.format(voltage), '{}V'.format(voltage)]]
                elif self.data_key == 1:
                    temp = int(databyte) / 2
                    data = [2, ['Temperature {}C'.format(temp), 'Temp: {}C'.format(temp), '{}C'.format(temp)]]
                elif self.data_key == 2:
                    self.work_var = databyte  # Get first 8 bits of flavor
                elif self.data_key == 3:
                    flavor = int((self.work_var << 8) | databyte)  # Append new databyte to end of old
                    data = [3, ['Firmware flavor: {}'.format(flavor), 'Flavor: {}'.format(flavor), 'Flavor']]
                elif self.data_key == 4:
                    self.work_var = int(databyte)  # Minor version
                elif self.data_key == 5:
                    version = '{}{}'.format(chr(databyte), self.work_var)
                    data = [3, ['Firmware version: {}'.format(version), 'Version: {}'.format(version), 'Version']]
        return data

    def update_state(self, ss):
        if self.is_writing:
            pass
        else:
            if self.curr_chip == PIC:
                if self.data_key in (0, 1, 2, 4):
                    self.ann_start_pos = ss
        self.data_key += 1

    def decode(self, ss, es, data):
        command, databyte = data

        if command == 'ADDRESS WRITE':
            self.curr_chip = CHIP_MAP.get(databyte)
            self.data_key = 0
            self.is_writing = True

            if self.show_curr_chip():
                chipname = self.curr_chip.value
                self.put_ann(ss, es, [0, ['Writing to chip: {}'.format(chipname), 'Write chip {}'.format(chipname),
                                          'Write {}'.format(chipname), 'W {}'.format(chipname), 'WC']])
        elif command == 'ADDRESS READ':
            self.curr_chip = CHIP_MAP.get(databyte)
            self.data_key = 0
            self.is_writing = False

            if self.show_curr_chip():
                chipname = self.curr_chip.value
                self.put_ann(ss, es, [0, ['Reading from chip: {}'.format(chipname), 'Read chip {}'.format(chipname),
                                          'Read {}'.format(chipname), 'R {}'.format(chipname), 'RC']])
        elif self.show_curr_chip():
            if command == 'DATA READ':
                data = self.get_data_ann(databyte)
                self.update_state(ss)
                self.put_ann(self.ann_start_pos, es, data)
            elif command == "NACK":
                pass
            self.put_ann(ss, es, [11, ['{}'.format(es - ss), ]])
# END OF FILE
