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


def reg_list():
    l = []
    for i in range(8 + 1):
        l.append(('reg-0x%02x' % i, 'Register 0x%02x' % i))
    return tuple(l)


class Task(Enum):
    IDLE = 0
    GET_SLAVE_ADDR = 1
    GET_REG_ADDR = 2
    WRITE_REGS = 3
    READ_REGS = 4
    START_REPEAT = 5
    READ_REGS2 = 6


IDLE = Task.IDLE
GET_SLAVE_ADDR = Task.GET_SLAVE_ADDR
GET_REG_ADDR = Task.GET_REG_ADDR
WRITE_REGS = Task.WRITE_REGS
READ_REGS = Task.READ_REGS
START_REPEAT = Task.START_REPEAT
READ_REGS2 = Task.READ_REGS2

# these aren't being used because it caused some sort of problem I think,
# it would be nice to not have to have the hard coded below though.
pic_address = 0x50
usb_address = 0x28
hall_address = 0x5E
bms_address = 0x0B

chip_map = {pic_address: 'PIC', usb_address: 'USB-PD_IC', hall_address: 'Hall', bms_address: 'BMS'}

class Decoder(srd.Decoder):
    api_version = 3
    id = 'lmi_reflex'
    name = 'LMI_Reflex'
    longname = 'LMI Reflex'
    desc = 'i2c decoder for LMI Reflex'
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
         'values': ('yes', 'no')}
    )
    annotations = reg_list() + (  # 0-8
        ('read', 'Read date/time'),  # 9
        ('write', 'Write date/time'),  # 10
        ('bit-reserved', 'Reserved bit'),  # 11
        ('bit-vl', 'VL bit'),  # 12
        ('bit-century', 'Century bit'),  # 13
        ('reg-read', 'Register read'),  # 14
        ('reg-write', 'Register write'),  # 15
        ('chip-select', 'Chip select'),  # 16
    )
    annotation_rows = (
        ('regs', 'Register accesses', (14, 15)),
        ('date-time', 'Date/time', (9, 10)),
        ('chip-sel', 'Chip select', (16,))
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = IDLE
        self.curslave = -1
        self.bits = []

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def putx(self, data):
        self.put(self.start_sample, self.end_sample, self.out_ann, data)

    def check_correct_chip(self):
        if (self.curslave == pic_address) and (self.options['PIC'] == 'no'):
            self.state = IDLE
        if (self.curslave == usb_address) and (self.options['USB-PD-IC'] == 'no'):
            self.state = IDLE
        if (self.curslave == hall_address) and (self.options['Hall'] == 'no'):
            self.state = IDLE
        if (self.curslave == bms_address) and (self.options['BMS'] == 'no'):
            self.state = IDLE

    def decode(self, ss, es, data):
        cmd, databyte = data

        # Store the start/end samples of this I²C packet.
        self.start_sample, self.end_sample = ss, es

        # Collect the 'BITS' packet, then return. The next packet is
        # guaranteed to belong to these bits we just stored.
        if cmd == 'BITS':
            #    self.bits = databyte
            return

        # State machine.    
        if self.state == IDLE:
            # Wait for an I²C START condition.
            if cmd != 'START':
                return
            self.state = GET_SLAVE_ADDR
            self.start_cond_loc = ss

        elif self.state == GET_SLAVE_ADDR:
            self.curslave = databyte
            slave_name = chip_map.get(databyte)
            self.putx([16, ['Chip selected: %s' % slave_name, 'Chip sel: %s' % slave_name,
                            'CS %s' % slave_name, 'CS', 'C']])
            self.state = GET_REG_ADDR

        elif self.state == GET_REG_ADDR:
            # Wait for a data write (master selects the slave register).
            if cmd == 'DATA WRITE':
                self.state = WRITE_REGS
            elif cmd == 'DATA READ':
                self.state = READ_REGS
            else:
                return
            self.check_correct_chip()
            self.reg = databyte
            
        elif self.state == WRITE_REGS:
            # If we see a Repeated Start here, it's probably an RTC read.
            if cmd == START_REPEAT:
                self.state = START_REPEAT
                return
            # Otherwise: Get data bytes until a STOP condition occurs.
            elif cmd == 'DATA WRITE':
                r, s = self.reg, '%02X: %02X' % (self.reg, databyte)
                self.putx([15, ['Write register %s' % s, 'Write reg %s' % s,
                                'WR %s' % s, 'WR', 'W']])
                handle_reg = getattr(self, 'handle_reg_0x%02x' % self.reg)
                handle_reg(databyte)
                self.reg += 1
                # TODO: Check for NACK!
            elif cmd == 'STOP':
                # TODO: Handle read/write of only parts of these items.
                d = '%02X' % (self.curslave)
                self.put(self.start_cond_loc, es, self.out_ann,
                         [9, ['Write addr: %s' % d, 'Write: %s' % d,
                              'W: %s' % d]])
                self.state = IDLE

        elif self.state == READ_REGS:
            if cmd == 'DATA READ':
                r, s = self.reg, '%02X: %02X' % (self.reg, databyte)
                self.putx([15, ['Read register %s' % s, 'Read reg %s' % s,
                                'RR %s' % s, 'RR', 'R']])
                handle_reg = getattr(self, 'handle_reg_0x%02x' % self.reg)
                handle_reg(databyte)
                self.reg += 1
            elif cmd == 'STOP':
                d = '%02X' % (self.curslave)
                self.put(self.start_cond_loc, es, self.out_ann,
                         [10, ['Read addr: %s' % d, 'Read: %s' % d,
                               'R: %s' % d]])
                self.state = IDLE
                self.curslave = -1

        elif self.state == START_REPEAT:
            # Wait for an address read operation.
            if cmd == 'ADDRESS READ':
                self.state = READ_REGS2
                self.curslave = databyte

        elif self.state == READ_REGS2:
            if cmd == 'DATA READ':
                r, s = self.reg, '%02X: %02X: %02X' % (self.curslave, self.reg, databyte)
                self.putx([15, ['Read2 register %s' % s, 'Read reg %s' % s,
                                'RR %s' % s, 'RR', 'R']])
                handle_reg = getattr(self, 'handle_reg_0x%02x' % self.reg)
                handle_reg(databyte)
                self.reg += 1
                # TODO: Check for NACK!
            elif cmd == 'STOP':
                d = '%02X' % (self.curslave)
                self.put(self.start_cond_loc, es, self.out_ann,
                         [10, ['Read2 reg addr: %s' % d, 'Read: %s' % d,
                               'R: %s' % d]])
                self.state = IDLE
                self.curslave = -1
                 