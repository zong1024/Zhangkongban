__version__ = "MuVisionSensor v0.2.3"
__author__ = "weiyanfengv@gmail.com"
__license__ = "http://unlicense.org"

import ustruct  # pylint: disable=import-error
from time import sleep_ms  # pylint: disable=no-name-in-module
import time

MU_MAX_RESULT = 1
MU_DEVICE_ID = 0x03

# MuVisionType: Vision Type User Input
"""
* MuVisionType
* Bit: |          3             |            2               |            1             |           0         |
*      |  VISION_LINE_DETECT    |   VISION_BALL_DETECT       | VISION_COLOR_RECOGNITION | VISION_COLOR_DETECT |
*      |           7            |             6              |            5             |           4         |
*      | VISION_NUM_CARD_DETECT | VISION_TRAFFIC_CARD_DETECT | VISION_SHAPE_CARD_DETECT | VISION_BODY_DETECT  |
"""
VISION_COLOR_DETECT = 0x01
VISION_COLOR_RECOGNITION = 0x02
VISION_BALL_DETECT = 0x04
#VISION_LINE_DETECT = 0x08
VISION_BODY_DETECT = 0x10
VISION_SHAPE_CARD_DETECT = 0x20
VISION_TRAFFIC_CARD_DETECT = 0x40
VISION_NUM_CARD_DETECT = 0x80
VISION_ALL = 0xffff

# MuLightSensorType: light sensor user input
LS_PROXIMITY_ENABLE = 0x01
LS_AMBIENT_LIGHT_ENABLE = 0x02
LS_COLOR_ENABLE = 0x04
LS_GESTURE_ENABLE = 0x08

# Card Type
# Vision Shape Card
MU_SHAPE_CARD_TICK = 0x01
MU_SHAPE_CARD_CROSS = 0x02
MU_SHAPE_CARD_CIRCLE = 0x03
MU_SHAPE_CARD_SQUARE = 0x04
MU_SHAPE_CARD_TRIANGLE = 0x05

# Vision Traffic Card
MU_TRAFFIC_CARD_FORWARD = 0x01
MU_TRAFFIC_CARD_LEFT = 0x02
MU_TRAFFIC_CARD_RIGHT = 0x03
MU_TRAFFIC_CARD_TURN_AROUND = 0x04
MU_TRAFFIC_CARD_PARK = 0x05

# Vision Color Type
MU_COLOR_UNKNOWN = 0x00
MU_COLOR_BLACK = 0x01
MU_COLOR_WHITE = 0x02
MU_COLOR_RED = 0x03
MU_COLOR_YELLOW = 0x04
MU_COLOR_GREEN = 0x05
MU_COLOR_CYAN = 0x06
MU_COLOR_BLUE = 0x07
MU_COLOR_PURPLE = 0x08

# Error Type
MU_OK = 0x00
MU_FAIL = 0xF1
MU_WRITE_TIMEOUT = 0xF2
MU_READ_TIMEOUT = 0xF3
MU_CHECK_ERROR = 0xF4
MU_UNKNOW_PARAM = 0xF5
MU_UNKNOW_PROTOCOL = 0xF6
MU_SLAVE_OK = 0xE0
MU_SLAVE_FAIL = 0xE1
MU_SLAVE_UNKNOW = 0xE2
MU_SLAVE_TIMEOUT = 0xE3
MU_SLAVE_CHECK_ERROR = 0xE4
MU_SLAVE_LENGTH_ERROR = 0xE5
MU_SLAVE_UNKNOW_COMMAND = 0xE6
MU_SLAVE_UNKNOW_REG_ADDRESS = 0xE7
MU_SLAVE_UNKNOW_REG_VALUE = 0xE8
MU_SLAVE_READ_ONLY = 0xE9
MU_SLAVE_RESTART_ERROR = 0xEA

# Vision Ball Type
MU_BALL_TABLE_TENNIS = 0x01
MU_BALL_TENNIS = 0x02

# MuVsLedColor
LedClose = 0
LedRed = 1
LedGreen = 2
LedYellow = 3
LedBlue = 4
LedPurple = 5
LedCyan = 6
LedWhite = 7

# register address define
# MuVsRegAddress
RegDeviceId = 0x01
RegFirmwareVersion = 0x02
RegRestart = 0x03
RegSensorConfig1 = 0x04
RegLock = 0x05
RegLed1 = 0x06
RegLed2 = 0x07
RegLedLevel = 0x08
RegUart = 0x09
RegLightSensor = 0x0A
RegIO = 0x0B
RegBle = 0x0C
RegCameraConfig1 = 0x10
RegFrameCount = 0x1F
RegVisionId = 0x20
RegVisionConfig1 = 0x21
RegVisionConfig2 = 0x22
RegParamValue1 = 0x25
RegParamValue2 = 0x26
RegParamValue3 = 0x27
RegParamValue4 = 0x28
RegParamValue5 = 0x29
RegVisionStatus1 = 0x2A
RegVisionStatus2 = 0x2B
RegVisionDetect1 = 0x30
RegVisionDetect2 = 0x31
RegResultNumber = 0x34
RegResultId = 0x35
RegReadStatus1 = 0x36
RegResultData1 = 0x40
RegResultData2 = 0x41
RegResultData3 = 0x42
RegResultData4 = 0x43
RegResultData5 = 0x44
RegLsProximity = 0x50
RegLsAlsL = 0x51
RegLsAlsH = 0x52
RegLsRawColorRedL = 0x53
RegLsRawColorRedH = 0x54
RegLsRawColorGreenL = 0x55
RegLsRawColorGreenH = 0x56
RegLsRawColorBlueL = 0x57
RegLsRawColorBlueH = 0x58
RegLsColor = 0x59
RegLsGesture = 0x5A
RegLsColorRed = 0x60
RegLsColorGreen = 0x61
RegLsColorBlue = 0x62
RegLsColorHueL = 0x63
RegLsColorHueH = 0x64
RegLsColorSaturation = 0x65
RegLsColorValue = 0x66
RegSn = 0xD0

# MuVsLed
Led1 = 1
Led2 = 2
LedAll = 3

# MuVsBaudrate
Baud9600 = 0x00
Baud19200 = 0x01
Baud38400 = 0x02
Baud57600 = 0x03
Baud115200 = 0x04
Baud230400 = 0x05
Baud460800 = 0x06
Baud921600 = 0x07

# MuVsObjectInf
Status = 0x00  # whether the target is detected
XValue = 0x01  # target horizontal position
YValue = 0x02  # target vertical position
WidthValue = 0x03  # target width
HeightValue = 0x04  # target height
Label = 0x05  # target label
RValue = 0x06  # R channel value
GValue = 0x07  # G channel value
BValue = 0x08  # B channel value

# MuVsStreamOutputMode
# for UART mode only
CallBackMode = 0      # u need send a request first and wait for response
DataFlowMode = 1      # MU will automatically response the result of the vision that u enabled whether it detected or undetected
EventMode = 2      # MU can only automatically response the result of the vision that u enabled which detected target

# MuVsCameraZoom
ZoomDefault = 0
Zoom1 = 1
Zoom2 = 2
Zoom3 = 3
Zoom4 = 4
Zoom5 = 5

# MuVsCameraFPS
FPSNormal = 0          # 25FPS mode
FPSHigh = 1          # 50FPS mode

# MuVsCameraWhiteBalance
AutoWhiteBalance = 0    # auto white balance mode
# lock white balance with current value the entire process takes about 100ms
LockWhiteBalance = 1
WhiteLight = 2    # white light mode
YellowLight = 3    # yellow light mode

# MuVsVisionLevel
LevelDefault = 0
LevelSpeed = 1      # speed first mode
LevelBalance = 2      # balance mode
LevelAccuracy = 3      # accuracy first mode

# MuVsLsSensitivity
SensitivityDefault = 0
Sensitivity1 = 1
Sensitivity2 = 2
Sensitivity3 = 3

# MuVsLsGesture
GestureNone = 0
GestureUp = 1
GestureDown = 2
GestureRight = 3
GestureLeft = 4
GesturePush = 5
GesturePull = 6

# MuVsLsColorType
LsColorLabel = 0
LsColorRed = 1
LsColorGreen = 2
LsColorBlue = 3
LsColorHue = 4
LsColorSaturation = 5
LsColorValue = 6

# MuVsLsRawColorType
LsRawColorRed = 0
LsRawColorGreen = 1
LsRawColorBlue = 2


LOG_CRITICAL = 50
LOG_ERROR = 40
LOG_WARNING = 30
LOG_INFO = 20
LOG_DEBUG = 10
LOG_NOTSET = 0


class MuvisionLogger:

    _level = LOG_INFO
    _level_dict = {
        LOG_CRITICAL: "CRIT",
        LOG_ERROR: "ERROR",
        LOG_WARNING: "WARN",
        LOG_INFO: "INFO",
        LOG_DEBUG: "DEBUG",
    }

    def _level_str(self, level):
        l = self._level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        self._level = level

    def isEnabledFor(self, level):
        return level >= self._level

    def log(self, name, level, msg, *args):
        if self.isEnabledFor(level):
            levelname = self._level_str(level)
            msgformat = ["%s.%s:" % (name, levelname)]
            len_arg = len(args)

            if type(msg) == type("str") and len_arg > 0:
                len_msg = msg.count('%')
                if len_msg >= len_arg and len_msg > 0:
                    msgformat.append(msg % args)
                else:
                    msgformat.append(msg)
                    msgformat += args
            else:
                msgformat.append(msg)
                msgformat += args

            print(*msgformat, sep=" ")


class Muvision_result:
    result_data1 = 0
    result_data2 = 0
    result_data3 = 0
    result_data4 = 0
    result_data5 = 0


class MuVsVisionState:
    def __init__(self, vision_type):
        self.vision_type = vision_type
        self.frame = 0
        self.detect = 0
        self.vision_result = []

        for _ in range(MU_MAX_RESULT):
            self.vision_result.append(Muvision_result())


class MuVsI2CMethod:
    """

    """

    def __init__(self, address, communication_port, logger=None):
        self.__mu_address = address
        self.__communication_port = communication_port
        self.__logger = logger

        if address not in communication_port.scan():
            raise ValueError(
                "MuVsI2CMethod Init Error!!! address %#x cannot found!" % address)

    def Logger(self, *arg):  # level, format, args
        if self.__logger:
            self.__logger(self.__class__.__name__, *arg)

    def Set(self, reg_address, value):
        data = ustruct.pack("<b", value)
        self.__communication_port.writeto_mem(
            self.__mu_address, reg_address, data)

        self.Logger(LOG_DEBUG, "set-> reg:%#x var:%#x",
                    reg_address, value)

        return MU_OK

    def Get(self, reg_address):
        data = ustruct.pack("<b", reg_address)
        self.__communication_port.writeto(self.__mu_address, data)

        value = self.__communication_port.readfrom(
            self.__mu_address, 1)
        if value:
            self.Logger(LOG_DEBUG, "Get-> reg:%#x var:%#x",
                        reg_address, value[0])
            return (MU_OK, value[0])
        else:
            self.Logger(LOG_ERROR, "Get-> reg:%#x TimeOut!",
                        reg_address)

            return (MU_READ_TIMEOUT, 0)

    def Read(self, vision_id, vision_type):
        vision_state = MuVsVisionState(vision_type)
        err = self.Set(RegVisionId, vision_id)
        if err:
            return (err, vision_state)

        err, vision_state.frame = self.Get(RegFrameCount)
        if err:
            return (err, vision_state)

        err, vision_state.detect = self.Get(RegResultNumber)
        if err:
            return (err, vision_state)

        if not vision_state.detect:
            return (MU_OK, vision_state)

        vision_state.detect = MU_MAX_RESULT if MU_MAX_RESULT < vision_state.detect else vision_state.detect
        for i in range(vision_state.detect):
            err = self.Set(RegResultId, i+1)
            if err:
                return (err, vision_state)
            err, vision_state.vision_result[i].result_data1 = self.Get(
                RegResultData1)
            if err:
                return (err, vision_state)
            err, vision_state.vision_result[i].result_data2 = self.Get(
                RegResultData2)
            if err:
                return (err, vision_state)
            err, vision_state.vision_result[i].result_data3 = self.Get(
                RegResultData3)
            if err:
                return (err, vision_state)
            err, vision_state.vision_result[i].result_data4 = self.Get(
                RegResultData4)
            if err:
                return (err, vision_state)
            err, vision_state.vision_result[i].result_data5 = self.Get(
                RegResultData5)
            if err:
                return (err, vision_state)

        return (MU_OK, vision_state)


class MuVsUartMethod:
    """

    """
    START = 0xFF
    WRITE = 0x01
    WRITE_LEN = 0x08
    READ = 0x02
    READ_LEN = 0x07
    REQUEST = 0x12
    REQUEST_LEN = 0x07
    END = 0xED

    def __init__(self, address, communication_port, logger=None):
        self.__mu_address = address
        self.__communication_port = communication_port
        self.__logger = logger
        # Setting serial port parameters
        self.__communication_port.init(timeout=1000, timeout_char=10)

    def Logger(self, *arg):  # level, format, args
        if self.__logger:
            self.__logger(self.__class__.__name__, *arg)

    def __uart_read(self):

        count_ms = 0
        # The shortest receiving time of serial protocol is 6 bytes
        while self.__communication_port.any() < 6:
            count_ms += 1
            # The maximum waiting time for receiving data is 1s
            if count_ms < 1000:
                sleep_ms(1)
            else:
                return (MU_READ_TIMEOUT, [])

        self.Logger(LOG_DEBUG, "Waiting for reception takes %dms", count_ms)

        data_len = 0
        data_list = []
        for _ in range(self.__communication_port.any()):
            data_list.append(self.__communication_port.read(1)[0])
            if data_list[0] == self.START:
                data_list.append(self.__communication_port.read(1)[0])
                data_len = data_list[1]
                data_list += list(self.__communication_port.read(data_len-2))
                break

        if data_len > 0 and data_len == len(data_list):
            return (MU_OK, tuple(data_list))
        else:
            return (MU_UNKNOW_PROTOCOL, [])

    def __protocol_cheak(self, data):
        count = 0
        for i in data[:-2]:
            count += i
        count &= 0xff

        if self.END == data[-1] and count == data[-2]:
            return True
        else:
            return False

    def SetBuadrate(self, baud=Baud9600):
        baud_em = (Baud9600, Baud19200, Baud38400, Baud57600,
                   Baud115200, Baud230400, Baud460800, Baud921600)
        baud_se = (9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600)
        if baud in baud_em:
            i = baud_em.index(baud)
            self.Logger(LOG_INFO, "SetBuadrate:%d", baud_se[i])
            self.__communication_port.init(baudrate=baud_se[i])

    def Set(self, reg_address, value):
        cheak_num = (self.START+self.WRITE_LEN+self.__mu_address +
                     self.WRITE+reg_address+value) & 0xFF
        data_list = (self.START, self.WRITE_LEN, self.__mu_address,
                     self.WRITE, reg_address, value, cheak_num, self.END)

        data = ustruct.pack(">bbbbbbbb", *tuple(data_list))

        if self.__logger:
            self.Logger(LOG_DEBUG, "Set req-> %s",
                        ' '.join(['%02x' % b for b in data]))

        if self.__communication_port.any():
            # Clear cache before sending
            self.__communication_port.read()
        self.__communication_port.write(data)

        err, data = self.__uart_read()

        if self.__logger:
            self.Logger(LOG_DEBUG, "Set rev-> %s",
                        ' '.join(['%02x' % b for b in data]))

        if err:
            return err

        elif self.__protocol_cheak(tuple(data)):
            if data[3] != 0xE0:
                return data[3]
            else:
                return MU_OK
        else:
            return MU_CHECK_ERROR

    def Get(self, reg_address):
        cheak_num = (self.START+self.READ_LEN+self.__mu_address +
                     self.READ+reg_address) & 0xFF
        data_list = (self.START, self.READ_LEN, self.__mu_address,
                     self.READ, reg_address, cheak_num, self.END)

        data = ustruct.pack(">bbbbbbb", *tuple(data_list))

        if self.__logger:
            self.Logger(LOG_DEBUG, "Get req-> %s",
                        ' '.join(['%02x' % b for b in data]))

        if self.__communication_port.any():
            # Clear cache before sending
            self.__communication_port.read()
        self.__communication_port.write(data)
        err, data = self.__uart_read()

        if self.__logger:
            self.Logger(LOG_DEBUG, "Get rev-> %s",
                        ' '.join(['%02x' % b for b in data]))

        if err:
            return (err, 0)

        elif self.__protocol_cheak(tuple(data)):
            if data[3] != 0xE0:
                return (data[3], 0)
            else:
                return (MU_OK, data[5])

        else:
            return (MU_CHECK_ERROR, 0)

    def Read(self, vision_id, vision_type):
        vision_state = MuVsVisionState(vision_type)

        cheak_num = (self.START+self.REQUEST_LEN +
                     self.__mu_address+self.REQUEST+vision_id) & 0xFF
        data_list = (self.START, self.REQUEST_LEN, self.__mu_address,
                     self.REQUEST, vision_id, cheak_num, self.END)

        data = ustruct.pack(">bbbbbbb", *tuple(data_list))

        if self.__logger:
            self.Logger(LOG_DEBUG, "Read req-> %s",
                        ' '.join(['%02x' % b for b in data]))

        if self.__communication_port.any():
            # Clear cache before sending
            self.__communication_port.read()
        self.__communication_port.write(data)

        err, data = self.__uart_read()

        if self.__logger:
            self.Logger(LOG_DEBUG, "Read rev-> %s",
                        ' '.join(['%02x' % b for b in data]))

        if err:
            return (err, vision_state)

        elif self.__protocol_cheak(tuple(data)):
            if data[3] != 0x11:
                return (data[3], vision_state)
            elif data[5] != vision_id:
                return (MU_UNKNOW_PARAM, vision_state)
            else:
                vision_state.frame = data[4]
                vision_state.detect = data[6]
                vision_state.detect = MU_MAX_RESULT if MU_MAX_RESULT < vision_state.detect else vision_state.detect

                if not vision_state.detect:
                    return (MU_OK, vision_state)

                for i in range(vision_state.detect):
                    vision_state.vision_result[i].result_data1 = data[7+i*5]
                    vision_state.vision_result[i].result_data2 = data[8+i*5]
                    vision_state.vision_result[i].result_data3 = data[9+i*5]
                    vision_state.vision_result[i].result_data4 = data[10+i*5]
                    vision_state.vision_result[i].result_data5 = data[11+i*5]
                return (MU_OK, vision_state)
        else:
            return (MU_CHECK_ERROR, vision_state)


class MuVisionSensor:
    """

    """

    def __init__(self, address=0x60, debug=False):
        self.__address = address
        self.__mu_vs_method = None
        self.__output_mode = CallBackMode
        self.__vision_states = []
        self.__vision_types = (VISION_COLOR_DETECT,
                               VISION_COLOR_RECOGNITION,
                               VISION_BALL_DETECT,
                               # This item is not supported, temporarily blocked
                               0x800000,  # VISION_LINE_DETECT 不支持此项,暂时屏蔽
                               VISION_BODY_DETECT,
                               VISION_SHAPE_CARD_DETECT,
                               VISION_TRAFFIC_CARD_DETECT,
                               VISION_NUM_CARD_DETECT)
        self.SetDebug(debug)

    @staticmethod
    def __setLevel(*arg):
        pass

    def Logger(self, *arg):  # level, format, args
        if self.__logger:
            self.__logger(self.__class__.__name__, *arg)

    def SetDebug(self, debug=False, level=LOG_INFO):
        if debug:
            self.__debug = MuvisionLogger()
            self.__logger = self.__debug.log
            self.SetLogLevel = self.__debug.setLevel
            self.SetLogLevel(level)
        else:
            self.__logger = None
            self.SetLogLevel = self.__setLevel

    def __SensorLockReg(self, lock: bool):
        return self.__mu_vs_method.Set(RegLock, lock)

    def __ProtocolVersionCheck(self):
        err_count = 0

        while True:
            err_count += 1
            err, protocol_version = self.__mu_vs_method.Get(RegDeviceId)
            if (not err) and protocol_version == MU_DEVICE_ID:
                break
            if err_count > 3:
                return MU_UNKNOW_PROTOCOL

        # sensor set default if version is correction.
        return self.SensorSetDefault()

    def CameraGetAwb(self):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            pass

        return (camera_reg_value >> 5) & 0x03

    def CameraGetFPS(self):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            pass

        return (camera_reg_value >> 4) & 0x01

    def CameraGetRotate(self):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            pass

        return (camera_reg_value >> 3) & 0x01

    def CameraGetZoom(self):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            pass

        return camera_reg_value & 0x07

    def CameraSetAwb(self, awb):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            return err

        white_balance = (camera_reg_value >> 5) & 0x03

        if LockWhiteBalance == awb:
            camera_reg_value &= 0x1f
            camera_reg_value |= (awb & 0x03) << 5
            err = self.__mu_vs_method.Set(
                RegCameraConfig1, camera_reg_value)
            if err:
                return err
            while (camera_reg_value >> 7) == 0:
                err, camera_reg_value = self.__mu_vs_method.Get(
                    RegCameraConfig1)
                if err:
                    return err

        elif white_balance != awb:
            camera_reg_value &= 0x1f
            camera_reg_value |= (awb & 0x03) << 5
            err = self.__mu_vs_method.Set(
                RegCameraConfig1, camera_reg_value)
            if err:
                return err

        return err

    def CameraSetFPS(self, fps):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            return err

        gfps = (camera_reg_value >> 4) & 0x01
        if fps != gfps:
            camera_reg_value &= 0xef
            camera_reg_value |= (fps & 0x01) << 4
            err = self.__mu_vs_method.Set(
                RegCameraConfig1, camera_reg_value)
            if err:
                return err

        return err

    def CameraSetRotate(self, enable):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            return err

        rotate = (camera_reg_value >> 3) & 0x01
        if rotate != enable:
            camera_reg_value &= 0xf7
            camera_reg_value |= (enable & 0x01) << 3

            err = self.__mu_vs_method.Set(
                RegCameraConfig1, camera_reg_value)
            if err:
                return err

        return err

    def CameraSetZoom(self, zoom):

        err, camera_reg_value = self.__mu_vs_method.Get(
            RegCameraConfig1)
        if err:
            return err

        gzoom = camera_reg_value & 0x07

        if zoom != gzoom:
            camera_reg_value &= 0xf8
            camera_reg_value |= zoom & 0x07
            err = self.__mu_vs_method.Set(
                RegCameraConfig1, camera_reg_value)
            if err:
                return err

        return err

    def GetValue(self, vision_type, object_inf):
        '''
         Note: when getting the vision status, if the block is true, it will wait until the vision_type result is updated   
        '''
        check_vision_type = 0
        for vision_state in self.__vision_states:
            check_vision_type |= (vision_type & vision_state.vision_type)

        if check_vision_type != 0:
            if object_inf == Status:
                while True:
                    if (self.UpdateResult(vision_type, True) & vision_type) != 0:
                        break
                    else:
                        sleep_ms(10)  # pylint: disable=undefined-variable

            return self.__read(vision_type, object_inf)
        else:
            raise ValueError(
                "Vision_type is not enabled, please check the input:%#02x" % vision_type)

    def LedSetColor(self, led, detected_color, undetected_color, level):

        err, led_level = self.__mu_vs_method.Get(RegLedLevel)
        if err:
            return err

        if Led1 == led:
            address = RegLed1
            led_level &= 0xF0
            led_level |= (level & 0x0F)
            self.__mu_vs_method.Set(RegLedLevel, led_level)

        elif Led2 == led:
            address = RegLed2
            led_level &= 0x0F
            led_level |= (level << 4)
            self.__mu_vs_method.Set(RegLedLevel, led_level)

        elif LedAll == led:
            err = self.LedSetColor(Led1, detected_color,
                                   undetected_color, level)
            if err:
                return err
            err = self.LedSetColor(Led2, detected_color,
                                   undetected_color, level)
            return err

        else:
            return MU_UNKNOW_PARAM

        err, led_reg_value = self.__mu_vs_method.Get(address)

        if err:
            return err

        led_reg_value &= 0xf1
        led_reg_value |= (detected_color & 0x07) << 1

        led_reg_value &= 0x1f
        led_reg_value |= (undetected_color & 0x07) << 5

        err = self.__mu_vs_method.Set(address, led_reg_value)
        if err:
            return err

        return MU_OK

    def LedSetMode(self, led, manual: bool, hold: bool):

        if Led1 == led:
            address = RegLed1

        elif Led2 == led:
            address = RegLed2

        elif LedAll == led:
            err = self.LedSetMode(Led1, manual, hold)
            if err:
                return err
            err = self.LedSetMode(Led2, manual, hold)
            return err

        else:
            return MU_UNKNOW_PARAM

        err, led_reg_value = self.__mu_vs_method.Get(address)
        if err:
            return err

        gmanual = led_reg_value & 0x01
        ghold = (led_reg_value >> 4) & 0x01

        if manual != gmanual or hold != ghold:
            led_reg_value &= 0xfe
            led_reg_value |= manual & 0x01

            led_reg_value &= 0xef
            led_reg_value |= (hold & 0x01) << 4

            err = self.__mu_vs_method.Set(address, led_reg_value)
            if err:
                return err

        return MU_OK

    def SensorSetDefault(self):

        sensor_config_reg_value = 0x04
        default_setting = (sensor_config_reg_value >> 2) & 0x01

        err = self.__mu_vs_method.Set(RegSensorConfig1,
                                      sensor_config_reg_value)
        while default_setting:
            err, sensor_config_reg_value = self.__mu_vs_method.Get(
                RegSensorConfig1)
            if err:
                return err

            default_setting = (sensor_config_reg_value >> 2) & 0x01

        return err

    def SensorSetRestart(self):
        err = self.__mu_vs_method.Set(RegRestart, 1)
        if err:
            return err

        return MU_OK

    def SetValue(self, vision_type, object_inf, value):
        return self.__write(vision_type, object_inf, value)

    def UartSetBaudrate(self, baud):
        err, uart_reg_value = self.__mu_vs_method.Get(RegUart)
        baudrate = uart_reg_value & 0x07
        if (not err) and baudrate != baud:
            uart_reg_value &= 0xf8
            uart_reg_value |= baud & 0x07
            err = self.__mu_vs_method.Set(RegUart, uart_reg_value)
        if not err:
            if 'MuVsUartMethod' == self.__mu_vs_method.__class__.__name__:
                self.__mu_vs_method.SetBuadrate(baud)
                sleep_ms(500)

        return err

    def UpdateResult(self, vision_type, wait_all_result=True):
        vision_type_output = 0

        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                if 'MuVsUartMethod' == self.__mu_vs_method.__class__.__name__:
                    vision_id = 1 + \
                        self.__vision_types.index(vision_state.vision_type)
                    state_select = self.__vision_states.index(vision_state)

                    err, vision_state_temp = self.__mu_vs_method.Read(
                        vision_id, vision_state.vision_type)

                    if (not err) and vision_state.frame != vision_state_temp.frame:
                        self.__vision_states[state_select] = vision_state_temp
                    else:
                        return vision_type_output

                    vision_type_output = vision_type_output | vision_state.vision_type
                else:
                    err, frame = self.__mu_vs_method.Get(
                        RegFrameCount)
                    if err:
                        return vision_type_output

                    if vision_state.frame != frame:
                        vision_id = 1 + \
                            self.__vision_types.index(vision_state.vision_type)
                        state_select = self.__vision_states.index(vision_state)
                        self.__SensorLockReg(True)
                        err, vision_state = self.__mu_vs_method.Read(
                            vision_id, vision_state.vision_type)
                        if not err:
                            self.__vision_states[state_select] = vision_state
                        else:
                            self.__SensorLockReg(False)
                            return vision_type_output

                        vision_type_output = vision_type_output | vision_state.vision_type
                        self.__SensorLockReg(False)

        return vision_type_output

    def VisionBegin(self, vision_type):
        err = self.VisionSetStatus(vision_type, True)
        if err:
            return err

        # FIXME waiting for vision to initialize, may delete in later version
        sleep_ms(20)  # pylint: disable=undefined-variable
        err = self.VisionSetOutputMode(vision_type, CallBackMode)
        if err:
            return err

        return MU_OK

    def VisionEnd(self, vision_type):
        return self.VisionSetStatus(vision_type, False)

    def VisionGetLevel(self, vision_type):

        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                vision_id = 1 + \
                    self.__vision_types.index(vision_state.vision_type)
                self.__mu_vs_method.Set(RegVisionId, vision_id)
                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if not err:
                    return (vision_config_reg_value >> 4) & 0x03

        return LevelDefault

    def VisionGetOutputMode(self):
        return self.__output_mode

    def VisionGetStatus(self, vision_type):
        vision_status1 = 0
        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                vision_id = 1 + \
                    self.__vision_types.index(vision_state.vision_type)
                err = self.__mu_vs_method.Set(RegVisionId, vision_id)
                if err:
                    return 0
                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if err:
                    return 0
                status = vision_config_reg_value & 0x01
                vision_status1 |= status << (vision_id-1)

        return vision_type & vision_status1

    def VisionSetDefault(self, vision_type):

        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                vision_id = 1 + \
                    self.__vision_types.index(vision_state.vision_type)
                err = self.__mu_vs_method.Set(RegVisionId, vision_id)
                if err:
                    return err
                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if err:
                    return err

                vision_config_reg_value &= 0xfd
                vision_config_reg_value |= 0x01 << 1
                default_setting = (vision_config_reg_value >> 1) & 0x01
                err = self.__mu_vs_method.Set(RegVisionConfig1,
                                              vision_config_reg_value)
                if err:
                    return err

            while default_setting:
                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if err:
                    return err
                default_setting = (vision_config_reg_value >> 1) & 0x01

        return MU_OK

    def VisionSetLevel(self, vision_type,  level):

        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                vision_id = 1 + \
                    self.__vision_types.index(vision_state.vision_type)
                err = self.__mu_vs_method.Set(RegVisionId, vision_id)
                if err:
                    return err
                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if err:
                    return err
                glevel = (vision_config_reg_value >> 4) & 0x03
                if level != glevel:
                    vision_config_reg_value &= 0xcf
                    vision_config_reg_value |= (level & 0x03) << 4
                    err = self.__mu_vs_method.Set(RegVisionConfig1,
                                                  vision_config_reg_value)
                    if err:
                        return err

        return MU_OK

    def VisionSetOutputEnable(self, vision_type, status):

        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                vision_id = 1 + \
                    self.__vision_types.index(vision_state.vision_type)
                err = self.__mu_vs_method.Set(RegVisionId, vision_id)
                if err:
                    return err
                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if err:
                    return err
                output_enable = (vision_config_reg_value >> 7) & 0x01
                if output_enable != status:
                    vision_config_reg_value &= 0x7f
                    vision_config_reg_value |= (status & 0x01) << 7
                    err = self.__mu_vs_method.Set(RegVisionConfig1,
                                                  vision_config_reg_value)
                    if err:
                        return err

        return MU_OK

    def VisionSetOutputMode(self, vision_type, mode):

        self.__output_mode = mode
        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                vision_id = 1 + \
                    self.__vision_types.index(vision_state.vision_type)
                err = self.__mu_vs_method.Set(RegVisionId, vision_id)
                if err:
                    return err
                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if err:
                    return err
                output_mode = (vision_config_reg_value >> 2) & 0x03
                if output_mode != mode:
                    vision_config_reg_value &= 0xf3
                    vision_config_reg_value = (mode & 0x03) << 2
                    err = self.__mu_vs_method.Set(RegVisionConfig1,
                                                  vision_config_reg_value)
                    if err:
                        return err

        return MU_OK

    def VisionSetStatus(self, vision_type, enable: bool):

        for vision_type_select in self.__vision_types:
            if vision_type_select & vision_type:
                vision_id = 1+self.__vision_types.index(vision_type_select)

                err = self.__mu_vs_method.Set(RegVisionId, vision_id)
                if err:
                    return err

                err, vision_config_reg_value = self.__mu_vs_method.Get(
                    RegVisionConfig1)
                if err:
                    return err

                status = vision_config_reg_value & 0x01
                if status != enable:
                    vision_config_reg_value &= 0xfe
                    vision_config_reg_value |= enable & 0x01

                    err = self.__mu_vs_method.Set(
                        RegVisionConfig1, vision_config_reg_value)
                    if err:
                        return err
                if enable:
                    self.__vision_states.append(
                        MuVsVisionState(vision_type_select))
                else:
                    for mv_vision_state in self.__vision_states:
                        if vision_type_select == mv_vision_state.vision_type:
                            self.__vision_states.remove(mv_vision_state)

    def begin(self, communication_port=None):
        if "I2C" == communication_port.__class__.__name__:
            self.__mu_vs_method = MuVsI2CMethod(
                self.__address, communication_port, logger=self.__logger)
            self.Logger(LOG_INFO, "Begin I2C mode succeed!")

        elif 'UART' == communication_port.__class__.__name__:
            self.__mu_vs_method = MuVsUartMethod(
                self.__address, communication_port, logger=self.__logger)
            self.Logger(LOG_INFO, "Begin UART mode succeed!")

        elif communication_port == None:
            from machine import I2C, Pin  # pylint: disable=import-error
            communication_port = I2C(
                scl=Pin(Pin.P19), sda=Pin(Pin.P20), freq=400000)
            return self.begin(communication_port)

        else:
            return MU_UNKNOW_PARAM

        if self.__mu_vs_method:
            return self.__ProtocolVersionCheck()

        return MU_FAIL

    def __read(self, vision_type, object_inf, result_num=1):

        if (vision_type not in self.__vision_types) and object_inf != Status:
            return MU_UNKNOW_PARAM

        result_num = MU_MAX_RESULT if result_num > MU_MAX_RESULT else result_num
        result_num = (result_num-1) if result_num else 1

        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                if object_inf == Status:
                    return vision_state.detect
                elif object_inf == XValue:
                    return vision_state.vision_result[result_num].result_data1
                elif object_inf == YValue:
                    return vision_state.vision_result[result_num].result_data2
                elif object_inf == WidthValue:
                    return vision_state.vision_result[result_num].result_data3
                elif object_inf == HeightValue:
                    return vision_state.vision_result[result_num].result_data4
                elif object_inf == Label:
                    return vision_state.vision_result[result_num].result_data5
                elif object_inf == GValue:
                    return vision_state.vision_result[result_num].result_data1
                elif object_inf == RValue:
                    return vision_state.vision_result[result_num].result_data2
                elif object_inf == BValue:
                    return vision_state.vision_result[result_num].result_data3
                else:
                    return MU_UNKNOW_PARAM

        return MU_UNKNOW_PARAM

    def __write(self, vision_type, object_inf, value):

        if vision_type not in self.__vision_types:
            return MU_UNKNOW_PARAM

        vision_id = 1+self.__vision_types.index(vision_type)

        if object_inf == RValue or object_inf == XValue:
            address = RegParamValue1
        elif object_inf == GValue or object_inf == YValue:
            address = RegParamValue2
        elif object_inf == BValue or object_inf == WidthValue:
            address = RegParamValue3
        elif object_inf == HeightValue:
            address = RegParamValue4
        elif object_inf == Label:
            address = RegParamValue5
        else:
            return MU_FAIL

        err = self.__mu_vs_method.Set(RegVisionId, vision_id)
        if err:
            return err

        return self.__mu_vs_method.Set(address, value)

    def LsBegin(self, ls_type):
        err, ls_reg_value = self.__mu_vs_method.Get(RegLightSensor)
        if err:
            return err

        if ls_type == LS_GESTURE_ENABLE:
            ls_reg_value &= 0xf8
            self.Logger(LOG_WARNING, "JUST LS_GESTURE_ENABLE !")
        else:
            ls_type &= 0x07

        ls_reg_value |= ls_type
        err = self.__mu_vs_method.Set(RegLightSensor, ls_reg_value)
        return err

    def LsEnd(self, ls_type):
        ls_type = ~(ls_type & 0x0F)
        err, ls_reg_value = self.__mu_vs_method.Get(RegLightSensor)
        if err:
            return err
        ls_reg_value &= 0x0F
        ls_reg_value |= ls_type
        err = self.__mu_vs_method.Set(RegLightSensor, ls_reg_value)
        return err

    def LsSetSensitivity(self, sensitivity):

        err, ls_reg_value = self.__mu_vs_method.Get(RegLightSensor)

        ls_reg_value &= 0xcf
        ls_reg_value |= (sensitivity & 0x03) << 4

        err = self.__mu_vs_method.Set(RegLightSensor, ls_reg_value)
        return err

    def LsWhiteBalanceEnable(self, value: bool):

        err, ls_reg_value = self.__mu_vs_method.Get(RegLightSensor)

        ls_reg_value &= 0xbf
        ls_reg_value |= (value & 0x01) << 6

        err = self.__mu_vs_method.Set(RegLightSensor, ls_reg_value)
        if err:
            return err

        while True:
            err, ls_reg_value = self.__mu_vs_method.Get(
                RegLightSensor)
            if not (ls_reg_value >> 6) & 0x01 or err:
                break
        return err

    def LsReadProximity(self):
        _, proximity = self.__mu_vs_method.Get(RegLsProximity)
        return proximity

    def LsReadAmbientLight(self):
        _, alsl = self.__mu_vs_method.Get(RegLsAlsL)
        _, alsh = self.__mu_vs_method.Get(RegLsAlsH)
        return (alsh << 8 | alsl)

    def LsReadColor(self, color_t):
        if color_t == LsColorLabel:
            err, ret = self.__mu_vs_method.Get(RegLsColor)
        elif color_t == LsColorRed:
            err, ret = self.__mu_vs_method.Get(RegLsColorRed)
        elif color_t == LsColorGreen:
            err, ret = self.__mu_vs_method.Get(RegLsColorGreen)
        elif color_t == LsColorBlue:
            err, ret = self.__mu_vs_method.Get(RegLsColorBlue)
        elif color_t == LsColorHue:
            err, huel = self.__mu_vs_method.Get(RegLsColorHueL)
            err, hueh = self.__mu_vs_method.Get(RegLsColorHueH)
            ret = (hueh << 8 | huel)
        elif color_t == LsColorSaturation:
            err, ret = self.__mu_vs_method.Get(RegLsColorSaturation)
        elif color_t == LsColorValue:
            err, ret = self.__mu_vs_method.Get(RegLsColorValue)
        else:
            ret = 0
            err = MU_UNKNOW_PARAM

        if err:
            pass

        return ret

    def LsReadRawColor(self, color_t):
        if color_t == LsRawColorRed:
            _, retl = self.__mu_vs_method.Get(RegLsRawColorRedL)
            _, reth = self.__mu_vs_method.Get(RegLsRawColorRedH)

        elif color_t == LsRawColorGreen:
            _, retl = self.__mu_vs_method.Get(RegLsRawColorGreenL)
            _, reth = self.__mu_vs_method.Get(RegLsRawColorGreenH)

        elif color_t == LsRawColorBlue:
            _, retl = self.__mu_vs_method.Get(RegLsRawColorBlueL)
            _, reth = self.__mu_vs_method.Get(RegLsRawColorBlueH)

        return (reth << 8 | retl)

    def LsBeginGesture(self):
        _, ls_gesture_reg_value = self.__mu_vs_method.Get(
            RegLsGesture)

        ls_gesture_reg_value &= 0x7f
        ls_gesture_reg_value |= 0x80

        err = self.__mu_vs_method.Set(
            RegLsGesture, ls_gesture_reg_value)

        return err

    def LsReadGesture(self):
        MuVsLsGesture = (GestureUp,
                         GestureDown,
                         GestureLeft,
                         GestureRight,
                         GesturePush,
                         GesturePull)
        status = 1
        ls_gesture_reg_value = 0

        while status:
            err, ls_gesture_reg_value = self.__mu_vs_method.Get(
                RegLsGesture)

            if err:
                return GestureNone

            status = ls_gesture_reg_value >> 7

        gesture = ls_gesture_reg_value & 0xef
        if gesture in MuVsLsGesture:

            ls_gesture_reg_value &= 0x80
            ls_gesture_reg_value |= GestureNone & 0xef

            self.__mu_vs_method.Set(
                RegLsGesture, ls_gesture_reg_value)

            return gesture
        else:
            return GestureNone
