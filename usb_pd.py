class USB_PD:
    @staticmethod
    def write(decoder, databyte):
        data = []
        if databyte == 0x70:
            data = [24, ['USB-PD -> PDO number register', 'USB-PD -> PDO number', 'PDO number', 'PDO #']]
        elif databyte == 0x8D:
            data = [25, ['USB-PD -> PDO3 SNK 0 register', 'USB-PD -> PDO3 SNK 0', 'PDO3 SNK 0', 'PDO3 SNK']]
        elif databyte == 0x91:
            data = [26, ['USB-PD -> Register status 0', 'USB-PD -> Reg status 0', 'USB-PD -> Reg stat 0', 'REG STAT 0',
                         'REG STAT']]
        return data
