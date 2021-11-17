from aisutils import nmea
from aisutils import BitVector
from aisutils import binary

from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def acknowledge(self, data, interface):
        """Subclasses need to implement this method."""

class StandardStrategy(Strategy):
    def acknowledge(self, data, interface):
        try:
            interface.write(data)
        except Exception as e:
            print(e)
            return False

class AISStrategy(Strategy):
    def acknowledge(self, data, interface):
        try:
            if data.get("message_type") == 4:
                msg = '  ACK:' + str(data.get("dab_id")) + ',MSG:' + str(data.get("message_type")) + ',RSSI:' + str(data.get("dab_signal")) + ',SNR:-1'
            else:
                msg = '  ACK:' + str(data.get("dab_id")) + ',MSG:' + str(data.get("message_type")) + ''
            
            aisBits = BitVector.BitVector(textstring=msg)
            payloadStr, pad = binary.bitvectoais6(aisBits)  # [0]
            buffer = nmea.bbmEncode(1, 1, 0, 1, 8, payloadStr, pad, appendEOL=False)
            interface.write(buffer)
        except Exception as e:
            print(e)
            return False

class EthernetStrategy(Strategy):
    def acknowledge(self, data, interface):
        try:
            max_msg_length = 10 # The value is the amount of bytes the first message will be

            interface.init_socket(interface.ip_address, interface.socket_port)
            with interface.socket:
                interface.connect_socket() 
                interface.write(data, max_msg_length)
                reply = interface.read_socket(max_msg_length)
                return reply if not reply.get("reply") else False
        except Exception as e:
            print(e)
            return False