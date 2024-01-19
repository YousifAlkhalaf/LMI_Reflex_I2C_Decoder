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
    )
    annotation_rows = (
        ('chips', 'Chip info', (0,)),
        ('pic', 'PIC chip', (1, 2, 3, 4, 6, 7, 8, 9, 10)),
    )

    curr_chip = None
    is_writing = False
    data_key = 0
    ann_start_pos = 0
    out_ann = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.ann_start_pos = 0

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def put_ann(self, ssample, esample, data):
        self.put(ssample, esample, self.out_ann, data)

    def decode(self):
        pass

    def decode(self, ss, es, data):
        command, databyte = data

        if command == 'ADDRESS WRITE':
            chipname = CHIP_MAP.get(databyte).value
            self.put_ann(ss, es, [0, ['Writing to chip: %s' % chipname,
                                      'Write chip %s' % chipname, 'Write %s' % chipname, 'WC']])
        elif command == 'ADDRESS READ':
            chipname = CHIP_MAP.get(databyte).value
            self.put_ann(ss, es, [0, ['Reading from chip: %s' % chipname,
                                      'Read chip %s' % chipname, 'Read %s' % chipname, 'RC']])
