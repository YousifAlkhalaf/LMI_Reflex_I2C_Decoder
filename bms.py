class BMS:
    @staticmethod
    def write(decoder, databyte):
        data = []
        if decoder.data_key == 0:
            if decoder.prev_chip != decoder.curr_chip:
                decoder.curr_cmd = [databyte]
            if databyte == 0x0D:
                data = [11, ['BMS -> Get State Of Charge', 'Get SOC', 'SOC']]
            elif databyte == 0x44:
                data = [11, ['BMS -> ManufacturerBlockAccess', 'ManufactureAccess', 'MBAccess', 'MBA']]
            else:
                data = [11, ['Unknown', '?']]
        elif decoder.data_key == 1:
            decoder.curr_cmd.append(databyte)
            if databyte == 0x02:
                data = [12, ['ManufactureBlockAccess: Get Firmware Version', 'MAC: Get Firmware Version',
                             'Firmware Version', 'Firmware', 'FV']]
        elif decoder.data_key == 2:
            decoder.work_var = databyte
        elif decoder.data_key == 3:
            decoder.curr_cmd.append((databyte << 8) | decoder.work_var)
            if 0x0071 in decoder.curr_cmd:
                data = [12, ['DAStatus 1 (Voltages, Currents, Power)', 'DAStatus1', 'DA1']]
            elif 0x0072 in decoder.curr_cmd:
                data = [12, ['DAStatus 2 (Temperatures)', 'DAStatus2', 'DA2']]
            elif 0x0072 in decoder.curr_cmd:
                data = [12, ['ManufacturerInfo', 'MInfo']]

        return data

    @staticmethod
    def read(decoder, databyte):
        data = []
        if decoder.curr_cmd[0] == 0x0D:
            # ASK ABOUT FORMAT OF PERCENT!
            percent = 100 - int(databyte)
            data = [13, ['Battery percent: {}%'.format(percent), 'Battery: {}%'.format(percent), '{}%'.format(percent)]]
        elif decoder.curr_cmd[0] == 0x44:
            if 0x0071 in decoder.curr_cmd:
                data = BMS.da_status_1(decoder, databyte, decoder.data_key - 3)
            elif 0x0072 in decoder.curr_cmd:
                data = BMS.da_status_2(decoder, databyte, decoder.data_key - 3)
        else:
            data = [14, ['Byte number {}'.format(decoder.data_key + 1), 'Byte #: {}'.format(decoder.data_key + 1),
                         '{}'.format(decoder.data_key + 1)]]
        return data

    @staticmethod
    def da_status_1(decoder, databyte, da1_key):
        data = []
        if da1_key in range(0, 32, 2):
            decoder.work_var = databyte
        elif da1_key == 1:
            volts = int(databyte << 8 | decoder.work_var)
            volts /= 1000
            data = [14, ['Cell 1 Voltage: {}V'.format(volts), 'Cell 1: {}V'.format(volts), '{}V'.format(volts)]]
        elif da1_key == 3:
            volts = int(databyte << 8 | decoder.work_var)
            volts /= 1000
            data = [14, ['Cell 2 Voltage: {}V'.format(volts), 'Cell 2: {}V'.format(volts), '{}V'.format(volts)]]
        elif da1_key == 5:
            volts = int(databyte << 8 | decoder.work_var)
            volts /= 1000
            data = [14, ['Cell 3 Voltage: {}V'.format(volts), 'Cell 3: {}V'.format(volts), '{}V'.format(volts)]]
        elif da1_key == 7:
            volts = int(databyte << 8 | decoder.work_var)
            volts /= 1000
            data = [14, ['Cell 4 Voltage: {}V'.format(volts), 'Cell 4: {}V'.format(volts), '{}V'.format(volts)]]
        elif da1_key == 9:
            volts = int(databyte << 8 | decoder.work_var)
            volts /= 1000
            data = [15, ['BAT pin voltage: {} Volts'.format(volts), 'BAT voltage: {}V'.format(volts),
                         'BAT: {}V'.format(volts), '{}V'.format(volts)]]
        elif da1_key == 11:
            volts = int(databyte << 8 | decoder.work_var)
            volts /= 1000
            data = [16, ['PACK voltage: {} Volts'.format(volts), 'PACK: {} Volts'.format(volts),
                         'PACK: {}V'.format(volts), '{}V'.format(volts)]]
        elif da1_key == 13:
            amps = int(databyte << 8 | decoder.work_var)
            amps /= 1000
            data = [17, ['Cell 1 Current: {}A'.format(amps), 'Cell 1: {}A'.format(amps), '{}A'.format(amps)]]
        elif da1_key == 15:
            amps = int(databyte << 8 | decoder.work_var)
            amps /= 1000
            data = [17, ['Cell 2 Current: {}A'.format(amps), 'Cell 2: {}A'.format(amps), '{}A'.format(amps)]]
        elif da1_key == 17:
            amps = int(databyte << 8 | decoder.work_var)
            amps /= 1000
            data = [17, ['Cell 3 Current: {}A'.format(amps), 'Cell 3: {}A'.format(amps), '{}A'.format(amps)]]
        elif da1_key == 19:
            amps = int(databyte << 8 | decoder.work_var)
            amps /= 1000
            data = [17, ['Cell 4 Current: {}A'.format(amps), 'Cell 4: {}A'.format(amps), '{}A'.format(amps)]]
        elif da1_key == 21:
            watts = int(databyte << 8 | decoder.work_var)
            watts /= 100
            data = [18, ['Cell 1 Power: {}W'.format(watts), 'Cell 1: {}W'.format(watts), '{}W'.format(watts)]]
        elif da1_key == 23:
            watts = int(databyte << 8 | decoder.work_var)
            watts /= 100
            data = [18, ['Cell 2 Power: {}W'.format(watts), 'Cell 2: {}W'.format(watts), '{}W'.format(watts)]]
        elif da1_key == 25:
            watts = int(databyte << 8 | decoder.work_var)
            watts /= 100
            data = [18, ['Cell 3 Power: {}W'.format(watts), 'Cell 3: {}W'.format(watts), '{}W'.format(watts)]]
        elif da1_key == 27:
            watts = int(databyte << 8 | decoder.work_var)
            watts /= 100
            data = [18, ['Cell 4 Power: {}W'.format(watts), 'Cell 4: {}W'.format(watts), '{}W'.format(watts)]]
        elif da1_key == 29:
            watts = int(databyte << 8 | decoder.work_var)
            watts /= 100
            data = [18, ['Calculated Power: {}W'.format(watts), 'Curr Power: {}W'.format(watts), '{}W'.format(watts)]]
        elif da1_key == 31:
            watts = int(databyte << 8 | decoder.work_var)
            watts /= 100
            data = [18, ['Average Power: {}W'.format(watts), 'Avg Power: {}W'.format(watts), '{}W'.format(watts)]]

        return data

    @staticmethod
    def da_status_2(decoder, databyte, da2_key):
        temp = 0
        data = []
        if da2_key in range(0, 32, 2):
            decoder.work_var = databyte
        else:
            temp = BMS.get_temp(databyte, decoder)
        if da2_key == 1:
            data = [20, ['BMS Internal Temperature: {}K'.format(temp), 'Internal Temp: {}K'.format(temp),
                         'Int Temp: {}K'.format(temp), 'Int: {}K'.format(temp), '{}K'.format(temp)]]
        elif da2_key == 3:
            data = [21, ['TS1 Temperature: {}K'.format(temp), 'TS1 Temp: {}K'.format(temp), 'TS1: {}K'.format(temp),
                         '{}K'.format(temp)]]
        elif da2_key == 5:
            data = [21, ['TS2 Temperature: {}K'.format(temp), 'TS2 Temp: {}K'.format(temp), 'TS2: {}K'.format(temp),
                         '{}K'.format(temp)]]
        elif da2_key == 7:
            data = [21, ['TS3 Temperature: {}K'.format(temp), 'TS3 Temp: {}K'.format(temp), 'TS3: {}K'.format(temp),
                         '{}K'.format(temp)]]
        elif da2_key == 9:
            data = [21, ['TS4 Temperature: {}K'.format(temp), 'TS4 Temp: {}K'.format(temp), 'TS4: {}K'.format(temp),
                         '{}K'.format(temp)]]
        elif da2_key == 11:
            data = [22, ['Cell Temperature: {}K'.format(temp), 'Cell Temp: {}K'.format(temp), 'Cell: {}K'.format(temp),
                         '{}K'.format(temp)]]
        elif da2_key == 13:
            data = [23, ['FET Temperature: {}K'.format(temp), 'FET Temp: {}K'.format(temp), 'FET: {}K'.format(temp),
                         '{}K'.format(temp)]]
        return data

    @staticmethod
    def get_temp(databyte, decoder):
        return int(databyte << 8 | decoder.work_var) / 10
