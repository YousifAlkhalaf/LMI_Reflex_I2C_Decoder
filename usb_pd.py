class USB_PD:
    @staticmethod
    def write(decoder, databyte):
        data = []
        decoder.curr_cmd = databyte
        if databyte == 0x70:
            data = [24, ['USB-PD -> PDO number register', 'USB-PD -> PDO number', 'PDO number', 'PDO #']]
        elif databyte == 0x8D:
            data = [24, ['USB-PD -> PDO3 SNK 0 register', 'USB-PD -> PDO3 SNK 0', 'PDO3 SNK 0', 'PDO3 SNK']]
        elif databyte == 0x91:
            data = [24, ['USB-PD -> Register status 0', 'USB-PD -> Reg status 0', 'USB-PD -> Reg stat 0', 'REG STAT 0',
                         'REG STAT']]
        return data

    @staticmethod
    def read(decoder, databyte):
        data = []
        if decoder.curr_cmd == 0x70:
            pdo_num = int(databyte & 0b00000111)
            data = [25, ['DPM_PDO_NUM: {}'.format(pdo_num), 'PDO NUM: {}'.format(pdo_num), 'PDO = {}'.format(pdo_num),
                         '{}'.format(pdo_num)]]
        elif decoder.curr_cmd == 0x8D:
            data = USB_PD.pdo_sink_read(databyte, decoder)
        elif decoder.curr_cmd == 0x91:
            data = USB_PD.rdo_reg_status_read(databyte, decoder)
        return data

    @staticmethod
    def pdo_sink_read(databyte, decoder):
        data = []
        if decoder.data_key == 0:
            decoder.work_var = databyte
        elif decoder.data_key == 1:
            decoder.work_var = databyte << 8 | decoder.work_var
        elif decoder.data_key == 2:
            decoder.work_var = databyte << 16 | decoder.work_var
        elif decoder.data_key == 3:
            decoder.work_var = databyte << 24 | decoder.work_var

            flags = []
            amps = USB_PD.get_current(decoder.work_var & 0x3FF)
            volts = USB_PD.get_voltage((decoder.work_var >> 10) & 0x3FF)

            # Checks reserved bits
            if (decoder.work_var >> 20 & 0b111) != 0:
                flags.append('Invalid')

            # Fast role swap required USB-Type-C current
            fast_swap = (decoder.work_var >> 23) & 0b11
            if fast_swap == 0b00:
                flags.append('Fast swap unsupported')
            elif fast_swap == 0b01:
                flags.append('Default USB power')
            elif fast_swap == 0b10:
                flags.append('1.5A at 5V')
            elif fast_swap == 0b11:
                flags.append('3.0A at 5V')

            if (decoder.work_var >> 25) & 0b1 == 0b1:
                flags.append('Dual role data')
            if (decoder.work_var >> 26) & 0b1 == 0b1:
                flags.append('USB communication capable')
            if (decoder.work_var >> 27) & 0b1 == 0b1:
                flags.append('Unconstrained power')
            if (decoder.work_var >> 28) & 0b1 == 0b1:
                flags.append('High capability')
            if (decoder.work_var >> 29) & 0b1 == 0b1:
                flags.append('Dual role power')

            flags.append('Fixed supply {}'.format(int(decoder.work_var >> 30)))

            data = [26, ['Operational current: {}A, Voltage: {}V, Flags: {}'.format(amps, volts, flags),
                         '{}A, {}V, Flags: {}'.format(amps, volts, flags),
                         '{}A, {}V, {} flags'.format(amps, volts, len(flags))]]
        return data

    @staticmethod
    def rdo_reg_status_read(databyte, decoder):
        data = []
        if decoder.data_key == 0:
            decoder.work_var = databyte
        elif decoder.data_key == 1:
            decoder.work_var = databyte << 8 | decoder.work_var
        elif decoder.data_key == 2:
            decoder.work_var = databyte << 16 | decoder.work_var
        elif decoder.data_key == 3:
            decoder.work_var = databyte << 24 | decoder.work_var

            max_amps = USB_PD.get_current(decoder.work_var & 0x3FF)
            amps = USB_PD.get_current(decoder.work_var >> 10 & 0x3FF)
            flags = []

            if (decoder.work_var >> 20 & 0b111) != 0 or (decoder.work_var >> 31) != 0:
                flags.append('Invalid')
            if decoder.work_var >> 23 & 0b1 == 1:
                flags.append('Unchunked extended messages supported')

            flags.append('No USB suspend' if decoder.work_var >> 24 & 0b1 == 1 else 'USB suspend')
            if (decoder.work_var >> 25) & 0b1 == 0b1:
                flags.append('USB communication capable')
            if (decoder.work_var >> 26) & 0b1 == 0b1:
                flags.append('Capability mismatch')
            if (decoder.work_var >> 27) & 0b1 == 0b0:
                flags.append('GiveBack enabled')
            object_pos = int((decoder.work_var >> 28) & 0b111)
            if object_pos != 0:
                flags.append('Object position {}'.format(object_pos))
            else:
                flags.append('Invalid object position')

            data = [27, ['Max operating current: {}A, Operating current: {}A, Flags: {}'.format(max_amps, amps, flags),
                         '{}A, {}A, Flags: {}'.format(max_amps, amps, flags),
                         '{}A, {}A, {} flags'.format(max_amps, amps, len(flags))]]

        return data

    @staticmethod
    def get_current(databyte):
        return int(databyte) / 100

    @staticmethod
    def get_voltage(databyte):
        return int(databyte) / 20
