class Hall:
    @staticmethod
    def read(decoder, databyte):
        if decoder.data_key > 7:
            return [27, ['Padding', '---', '-']]
        else:
            mag_flux_density = Hall.get_mag_flux_density(databyte)
            return [26, ['Magnetic flux density: {}mT'.format(mag_flux_density),
                         'Mag flux density: {}mT'.format(mag_flux_density), 'MFD: {}mT'.format(mag_flux_density),
                         '{}mT'.format(mag_flux_density)]]

    # Returns magnetic flux in milliteslas
    @staticmethod
    def get_mag_flux_density(databyte):
        measure = int(databyte & 0b01111111)
        if databyte & 0b10000000:
            measure -= 128
        return measure
