class Encrytor:
    @staticmethod
    def Encrypt(msg: str):
        return ''.join(format(ord(x), '08b') for x in msg)

    @staticmethod
    def BinaryToDecimal(binary):
        string = int(binary, 2)
        return string

    @staticmethod
    def Decrypt(msg: str):
        str_data = ''
        for i in range(0, len(msg), 8):
            temp_data = msg[i:i + 8]
            decimal_data = Encrytor.BinaryToDecimal(temp_data)
            str_data = str_data + chr(decimal_data)
        return str_data
