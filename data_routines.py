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
    def bms_read(decoder, databyte):
        pass
