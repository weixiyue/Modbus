"""constant defines """

""" Function Code Definition """
READ_COILS = 1  # 读线圈寄存器    Data Type: bit
READ_HOLDING_REGISTERS = 3  # 读保持寄存器    Data Type: int, float, string
WRITE_SINGLE_COIL = 5   # 写单个线圈寄存器  Data Type: bit

""" supported block types """
COILS = 1   # 线圈寄存器     Read/Write  operation: bit
DISCRETE_INPUTS = 2     # 离散输入寄存器   Read Only   operation: bit
HOLDING_REGISTERS = 3   # 保持寄存器     Read/Write  operation: word
ANALOG_INPUTS = 4       # 输入寄存器     Read Only   operation: word


""" modbus exception codes """
ILLEGAL_FUNCTION = 1
ILLEGAL_DATA_ADDRESS = 2
ILLEGAL_DATA_VALUE = 3
SLAVE_DEVICE_FAILURE = 4
COMMAND_ACKNOWLEDGE = 5
SLAVE_DEVICE_BUSY = 6
MEMORY_PARITY_ERROR = 8


# """ supported block types """
# COILS = 1
# DISCRETE_INPUTS = 2
# HOLDING_REGISTERS = 3
# ANALOG_INPUTS = 4
