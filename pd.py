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
from .pic import PIC as PIC_Routines
from .bms import BMS as BMS_Routines


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
        {'id': 'USB-PD-IC', 'desc': 'Display USB PD IC traffic', 'default': 'no',
         'values': ('yes', 'no')},
        {'id': 'Hall', 'desc': 'Display Hall sensor traffic', 'default': 'no',
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
        ('bms_request', 'BMS data request'),  # 11
        ('bms_mac', 'BMS MAC command (ManufacturerBlockAccess)'),  # 12
        ('bms_charge', 'Battery percentage'),  # 13
        ('bms_cell_volts', 'Battery cell voltages'),  # 14
        ('bms_bat_volts', 'BMS BAT pin voltage'),  # 15
        ('bms_pack_volts', 'BMS PACK voltage'),  # 16
        ('bms_cell_amps', 'Battery cell current'),  # '17
        ('bms_cell_watts', 'Battery cell power'),  # 18
        ('bms_power', 'BMS power data'),  # 19
        ('bms_int_temp', 'BMS internal temperature'),  # 20
        ('bms_sensor_temp', 'Temperature sensor temps'),  # 21
        ('bms_cell_temp', 'Battery cell temperature'),  # 22
        ('bms_fet_temp', 'FET temperature')  # 23
    )
    annotation_rows = (
        ('chips', 'Chip info', (0,)),
        ('pic', 'PIC chip', (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)),
        ('bms', 'BMS chip (TI BQ4050)', (11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23))
        # ('usb', 'USB-PD-IC chip (STUSB4500)', (15,))
    )

    curr_chip = [PIC, False]
    prev_chip = None

    shown_chips = []
    data_key = 0
    ann_start_pos = 0
    curr_cmd = None  # Holds byte list representing desired commands
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
        return self.curr_chip[0] in self.shown_chips

    def get_data_ann(self, databyte):
        data = []
        if self.curr_chip[1]:
            if self.curr_chip[0] == PIC:
                data = PIC_Routines.write(self, databyte)
            elif self.curr_chip[0] == BMS:
                data = BMS_Routines.write(self, databyte)
            elif self.curr_chip[0] == USB:
                #data = DataRoutines.usb_write(self, databyte)
                pass
        else:
            if self.curr_chip[0] == PIC:
                data = PIC_Routines.read(self, databyte)
            elif self.curr_chip[0] == BMS:
                data = BMS_Routines.read(self, databyte)
            elif self.curr_chip[0] == USB:
                #data = DataRoutines.usb_read(self, databyte)
                pass
        return data

    def update_state(self, ss):
        if self.curr_chip[1]: # Writing to chip
            if self.curr_chip[0] == PIC:
                if self.data_key not in (0, 8):
                    self.ann_start_pos = ss
            elif self.curr_chip[0] == BMS:
                if self.data_key not in (3, 5):
                    self.ann_start_pos = ss
        else:
            if self.curr_chip[0] == PIC:
                if self.data_key not in (3, 5):
                    self.ann_start_pos = ss
            elif self.curr_chip[0] == BMS:
                if self.data_key not in range(2, 35, 2):
                    self.ann_start_pos = ss
        self.data_key += 1

    def decode(self, ss, es, data):
        command, databyte = data

        if command == 'ADDRESS WRITE':
            self.prev_chip = self.curr_chip
            self.curr_chip = [CHIP_MAP.get(databyte), True]
            self.data_key = 0

            if self.show_curr_chip():
                chipname = self.curr_chip[0].value
                self.put_ann(ss, es, [0, ['Writing to chip: {}'.format(chipname), 'Write chip {}'.format(chipname),
                                          'Write {}'.format(chipname), 'W {}'.format(chipname), 'WC']])
        elif command == 'ADDRESS READ':
            self.prev_chip = self.curr_chip
            self.curr_chip = [CHIP_MAP.get(databyte), False]
            self.data_key = 0

            if self.show_curr_chip():
                chipname = self.curr_chip[0].value
                self.put_ann(ss, es, [0, ['Reading from chip: {}'.format(chipname), 'Read chip {}'.format(chipname),
                                          'Read {}'.format(chipname), 'R {}'.format(chipname), 'RC']])
        elif self.show_curr_chip():
            if command == 'DATA READ':
                data = self.get_data_ann(databyte)
                self.update_state(ss)
                self.put_ann(self.ann_start_pos, es, data)
            elif command == 'DATA WRITE':
                data = self.get_data_ann(databyte)
                self.update_state(ss)
                self.put_ann(self.ann_start_pos, es, data)
            elif command == "NACK":
                pass
# END OF FILE
