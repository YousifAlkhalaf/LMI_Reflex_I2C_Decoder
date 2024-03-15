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

            amps = USB_PD.get_current(decoder.work_var & 0x3FF)
            volts = USB_PD.get_voltage(decoder.work_var & (0x3FF << 10))
            data = [26, ['{}A, {}V'.format(amps, volts)]]
        return data

    @staticmethod
    def get_current(databyte):
        return int(databyte) / 100

    @staticmethod
    def get_voltage(databyte):
        return int(databyte) / 20
