class DataRoutines:

    @staticmethod
    def pic_write(decoder, databyte):
        data = []
        if decoder.data_key == 1:
            lumens = 100 * int(databyte)
            data = [4, ['Lumens: {} lm'.format(lumens), '{} lm'.format(lumens), 'lm']]
        elif decoder.data_key == 2:
            pwm = int(databyte)
            data = [5, ['Fan motor PWM: {}'.format(pwm), 'Fan PWM: {}'.format(pwm), 'Fan']]
        elif decoder.data_key == 3:
            stops = int(databyte) // 10
            data = [6, ['Burst (stops): {}'.format(stops), 'Stops: {}'.format(stops), 'Stops']]
        elif decoder.data_key == 4:
            led_states = {0: 'Red', 1: 'Red', 2: 'Green', 3: 'Amber'}
            led = led_states.get(int(databyte))
            data = [7, ['LED color: {}'.format(led), 'LED: {}'.format(led), 'LED']]
        elif decoder.data_key == 5:
            flag_map = {0: 'Sleep', 1: 'HSS', 2: 'Mux', 3: 'Pro', 4: 'Burst_En', 5: 'Debug'}
            flag_list = []
            for i in range(5, -1, -1):
                bit = (databyte >> i) & 1
                if bit == 1:
                    flag_list.append(flag_map.get(i))
            data = [8, ['Flags: {}'.format(flag_list), 'Flags: {}'.format(len(flag_list)), 'Flags']]
        elif decoder.data_key == 6:
            pwm = int(databyte)
            data = [9, ['Burst PWM: {}'.format(pwm), 'Burst: {}'.format(pwm), 'Burst']]
        elif decoder.data_key == 7:
            decoder.work_var = int(databyte)  # First 8 bits of delay
        elif decoder.data_key == 8:
            delay = int((decoder.work_var << 8) | databyte)
            data = [10, ['Burst delay: {}'.format(delay), 'Delay: {}'.format(delay), 'Delay']]
        return data

    @staticmethod
    def pic_read(decoder, databyte):
        data = []
        if decoder.data_key == 0:
            voltage = int(databyte) / 10
            data = [1, ['Voltage: {}V'.format(voltage), 'Volts: {}V'.format(voltage), '{}V'.format(voltage)]]
        elif decoder.data_key == 1:
            temp = int(databyte) / 2
            data = [2, ['Temperature {}C'.format(temp), 'Temp: {}C'.format(temp), '{}C'.format(temp)]]
        elif decoder.data_key == 2:
            decoder.work_var = databyte  # Get first 8 bits of flavor
        elif decoder.data_key == 3:
            flavor = int((decoder.work_var << 8) | databyte)  # Append new databyte to end of old
            data = [3, ['Firmware flavor: {}'.format(flavor), 'Flavor: {}'.format(flavor), 'Flavor']]
        elif decoder.data_key == 4:
            decoder.work_var = int(databyte)  # Minor version
        elif decoder.data_key == 5:
            version = '{}{}'.format(chr(databyte), decoder.work_var)
            data = [3, ['Firmware version: {}'.format(version), 'Version: {}'.format(version), 'Version']]
        return data

    @staticmethod
    def bms_write(decoder, databyte):
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

        return data

    @staticmethod
    def bms_read(decoder, databyte):
        data = []
        if decoder.curr_cmd[0] == 0x0D:
            # ASK ABOUT FORMAT OF PERCENT!
            percent = 100 - int(databyte)
            data = [13, ['Battery percent: {}%'.format(percent), 'Battery: {}%'.format(percent), '{}%'.format(percent)]]
        elif decoder.curr_cmd[0] == 0x44:
            if 0x0071 in decoder.curr_cmd:
                data = DataRoutines.bms_da_status_1(decoder, databyte, decoder.data_key-3)


        else:
            data = [14, ['Byte number {}'.format(decoder.data_key + 1), 'Byte #: {}'.format(decoder.data_key + 1),
                         '{}'.format(decoder.data_key + 1)]]
        return data

    @staticmethod
    def bms_da_status_1(decoder, databyte, da1_key):
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

    # @staticmethod
    # def usb_write(decoder, databyte):
    #     data = [99, ['FIND ME!', '!!!', '!']]
    #     return data
    #
    # @staticmethod
    # def usb_read(decoder, databyte):
    #     data = [99, ['FIND ME!', '!!!', '!']]
    #     return data
