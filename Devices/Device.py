#!/usr/bin/python
from Devices.Strategy import AISStrategy, EthernetStrategy, I2CStrategy, SPIStrategy
from Interface.I2C import I2C
from Interface.Ethernet import Ethernet
from Interface.UART import UART
from Interface.SPI import SPI

class Device:
    """A Class to represent the device that is responsible for acknowledging a message."""
    
    def __init__(self, name, branch, model, interface_type, technology, priority):
        self.name = name
        self.branch = branch
        self.model = model
        self.technology = technology
        self.priority = priority
        self.strategy = self.set_strategy_based_on_interface_type(interface_type)
    
    """
        This method is used to acknowledge a message using this device. 
        The method uses the strategy that belongs to the interface used by the device
    """
    def acknowledge(self, data):
        print("Confirming DAB message with dab_id: {}".format(data.get("dab_id")))
        return self.strategy.communicate(data, self.interface)

    """
        This method tries to determine if the device connected this object is within reach of a receiver.
        Is implemented for devices using AIS or Ethernet as Interface
    """
    def has_reach(self):
        # If the technology cannot confirm that there is a receiver in reach. Return None
        if isinstance(self.strategy, AISStrategy):
            return None
        elif isinstance(self.strategy, EthernetStrategy):
            data = {"has_reach": self.technology} # A dict to ask the fipy if the technology has_reach

            print("Asking for has_reach using the interface {} and technology {}".format(self.interface.__class__.__name__, self.technology))
            reply = self.strategy.communicate(data, self.interface)

            # reply is False if has_reach failes due to the reach of the technology or an error occuring. If so return False
            if not reply:
                return False

            if reply.get("reply") is True:
                return True
            else:
                # reply is False if has_reach failes due to the reach of the technology or an error occuring
                return False
        elif isinstance(self.strategy, I2CStrategy):
            """
                data = [1] means that it will ask the sodaq one if it has a connection with TTN or not?
                reply will be 0, 1 or False
            """
            reply = self.strategy.communicate(data=[1])
            
            # 0 will evaluate False and return False. While 1 evaluates True and returns True
            return True if reply else False
        else:
            print("Unknown strategy to device.has_reach()!")
            return False

    def set_strategy_based_on_interface_type(self, interface_type):
        if interface_type == 0:
            return AISStrategy()
        elif interface_type == 1:
            return I2CStrategy()
        elif interface_type == 2:
            return EthernetStrategy()
        elif interface_type == 3:
            return SPIStrategy()
        else:
            return None
        
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def get_strategy(self):
        return self.strategy

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_branch(self):
        return self.branch

    def set_branch(self, new_branch):
        self.branch = new_branch

    def get_model(self):
        return self.model

    def set_model(self, new_model):
        self.model = new_model
    
    def get_technology(self):
        return self.technology
    
    def set_technology(self, new_technology):
        self.technology = new_technology


'''
AIS device with interface
'''
# name, branch, model, port, type
#p1 = Device("AIS Transponder1", "True Heading", "AIS Base Station", 0)
# p1.setport("/dev/ttyUSB0")
# p1.init_serial(38400, 8, serial.STOPBITS_ONE)
# p1.check_connection_rs232()
#p1.init_i2c()
#p1.list_i2c()
#p1.close_rs232()
# p1.intf.setport("/dev/ttyUSB0")
# p1.intf.init_serial(38400, 8, serial.STOPBITS_ONE)
# p1.intf.checkconnection()
# msg = p1.encode_BBM(0)
#p1.intf.write(msg)


# aisin = interf.Interface(p1.name, p1.type)
# aisin.setport("/dev/ttyUSB0")
# aisin.init_serial(38400, 8, serial.STOPBITS_ONE)
# print(aisin.checkconnection())
# print(aisin.read())

#p1.getname()