__version__ = "MuVisionSensor3AT v0.2.4"
__author__ = "weiyanfengv@gmail.com"
__license__ = "http://unlicense.org"

from time import sleep_ms  # pylint: disable=no-name-in-module

MU_MAX_RESULT = 1
MU_DEVICE_ID = 0x03

VISION_COLOR_DETECT = 0x01
VISION_COLOR_RECOGNITION = 0x02
VISION_BALL_DETECT = 0x04
VISION_BODY_DETECT = 0x10
VISION_SHAPE_CARD_DETECT = 0x20
VISION_TRAFFIC_CARD_DETECT = 0x40
VISION_NUM_CARD_DETECT = 0x80
VISION_ALL = 0xffff

# CMD
MU_AT_OK = "OK\r\n"
MU_AT_OK_b = b"OK\r\n"
MU_AT_ERROR = "ERROR\r\n"
MU_AT_ERROR_b = b"ERROR\r\n"
MU_AT_VISION = "MUVISION"
MU_AT_WRITE = "MUWRITE"
MU_AT_ZOOM = "MUZOOM"
MU_AT_AWB = "MUAWB"
MU_AT_ROTATE = "MUROTATE"
MU_AT_FPS = "MUHFPS"
MU_AT_LED = "MULED"
MU_AT_LEVEL = "MULEVEL"
MU_AT_DEFAULT = "MUDEF"
MU_AT_UARTBAUD = "UARTBAUD"
MU_AT_READ = "MUREAD"
# Wifi
MU_AT_WIFISET = "WIFISET"
MU_AT_WIFICON = "WIFICON"
MU_AT_WIFISIP = "WIFISIP"
MU_AT_WIFICIP = "WIFICIP"
MU_AT_WIFIUDP = "WIFIUDP"
# Query
MU_AT_QUERY = "?"

# Error object_inf
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

# MuVsCameraZoom
ZoomDefault = "0"
Zoom1 = "1"
Zoom2 = "2"
Zoom3 = "3"
Zoom4 = "4"
Zoom5 = "5"

# MuVsCameraFPS
FPSNormal = "0"          # 25FPS mode
FPSHigh = "1"          # 50FPS mode

# MuVsCameraWhiteBalance
AutoWhiteBalance = "AUTO"    # auto white balance mode
# lock white balance with current value the entire process takes about 100ms
LockWhiteBalance = "LOCK"
WhiteLight = "WHITE"    # white light mode
YellowLight = "YELLOW"    # yellow light mode

# MuVsVisionLevel
LevelDefault = 0
LevelSpeed = 1      # speed first mode
LevelBalance = 2      # balance mode
LevelAccuracy = 3      # accuracy first mode

# MuVsLed
Led1 = "1"
Led2 = "2"
LedAll = "ALL"

# MuVsLedColor
LedClose = "0"
LedRed = "1"
LedGreen = "2"
LedYellow = "3"
LedBlue = "4"
LedPurple = "5"
LedCyan = "6"
LedWhite = "7"

# MuVsMessageVisionType
VisionColorDetect = "1"
VisionColorRecog = "2"
VisionBall = "3"
VisionBody = "5"
VisionShapeCard = "6"
VisionTrafficCard = "7"
VisionNumberCard = "8"

# MuVsBaudrate
Baud9600 = '0'
Baud19200 = '1'
Baud38400 = '2'
Baud57600 = '3'
Baud115200 = '4'
Baud230400 = '5'
Baud460800 = '6'
Baud921600 = '7'

# MuVsObjectInf
Status = '0'  # whether the target is detected
XValue = '1'  # target horizontal position
YValue = '2'  # target vertical position
WidthValue = '3'  # target width
HeightValue = '4'  # target height
Label = '5'  # target label
RValue = '6'  # R channel value
GValue = '7'  # G channel value
BValue = '8'  # B channel value

# MuVsVisionLevel
LevelSpeed = "1"      # speed first mode
LevelBalance = "2"      # balance mode
LevelAccuracy = "3"      # accuracy first mode

# wifi set mode
WifiModeSta = "STA"
WifiModeAp = "AP"

# wifi con status
WifiON = "1"
WifiOFF = "0"

# MuvisionLogger level
LOG_CRITICAL = 50
LOG_ERROR = 40
LOG_WARNING = 30
LOG_INFO = 20
LOG_DEBUG = 10
LOG_NOTSET = 0


class MuvisionLogger:

    _level = LOG_DEBUG
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


class MuVisionSensor3AT:

    def __init__(self, debug=False):
        self.__wifi_mode = WifiModeSta
        self.__vision_states = []
        self.__vision_types = (VISION_COLOR_DETECT,
                               VISION_COLOR_RECOGNITION,
                               VISION_BALL_DETECT,
                               # This item is not supported, temporarily blocked
                               0xff0000,  # VISION_LINE_DETECT 不支持此项,暂时屏蔽
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
            self.setLogLevel = self.__debug.setLevel
            self.setLogLevel(LOG_INFO)
        else:
            self.__logger = None
            self.setLogLevel = self.__setLevel

    def __SendATandRead(self, *pramas, **kwarg):
        """
        *pramas:Can accept multiple variable parameters, including query and settings
        **kwarg:The unique parameter 'nowait = true' can be set to not wait for the return value after sending the instruction. 
                It is used when WiFi set do connected.Other parameters should be false
        """
        if len(pramas) > 1:
            if pramas[1] != MU_AT_QUERY:
                new_pramas = []
                for pa in pramas[1:]:
                    pa = pa if type(pa) == type("str") else str(pa)
                    new_pramas.append(pa)

                prama_str = ",".join(new_pramas)
                at_cmd = "AT+{0}={1}\r\n".format(pramas[0], prama_str)
            else:
                at_cmd = "AT+{0}?\r\n".format(pramas[0])

        elif len(pramas) > 0:
            at_cmd = "AT+{0}\r\n".format(pramas[0])
        else:
            at_cmd = "AT\r\n"
        if self.__communication_port.any():
            # Clear cache before sending
            self.__communication_port.read()
        self.__communication_port.write(at_cmd)
        self.Logger(LOG_DEBUG, at_cmd)

        result = []
        value = MU_FAIL

        if kwarg.get("nowait") == True:
            return (MU_OK, "")

        while True:
            res = self.__communication_port.readline()
            if res == MU_AT_OK_b:
                value = MU_OK
                self.Logger(LOG_DEBUG, res)
                break
            elif res == MU_AT_ERROR_b:
                self.Logger(LOG_ERROR, "Read AT ERROR!")
                value = MU_UNKNOW_PARAM
                break
            elif not res:
                self.Logger(LOG_ERROR, "Read AT TimeOut!")
                value = MU_READ_TIMEOUT
                break
            self.Logger(LOG_DEBUG, res)
            result.append(res.decode())

        if value == MU_OK and len(result) > 0:
            if pramas[0] in result[-1]:
                res = result[-1].split(":")[-1]
                res = res.split("\r")[0]
                return (value, res)

            return (MU_UNKNOW_PARAM, "")
        else:
            return (value, "")

    def CameraGetAwb(self):
        _, res = self.__SendATandRead(MU_AT_AWB, MU_AT_QUERY)
        return res

    def CameraGetZoom(self):
        _, res = self.__SendATandRead(MU_AT_ZOOM, MU_AT_QUERY)
        return res

    def CameraGetRotate(self):
        _, res = self.__SendATandRead(MU_AT_ROTATE, MU_AT_QUERY)
        return res

    def CameraGetFPS(self):
        _, res = self.__SendATandRead(MU_AT_FPS, MU_AT_QUERY)
        return res

    def CameraSetAwb(self, awb):
        err, _ = self.__SendATandRead(MU_AT_AWB, awb)
        return err

    def CameraSetZoom(self, zoom):
        err, _ = self.__SendATandRead(MU_AT_ZOOM, zoom)
        return err

    def CameraSetRotate(self, status):
        err, _ = self.__SendATandRead(MU_AT_ROTATE, status)
        return err

    def CameraSetFPS(self, status):
        err, _ = self.__SendATandRead(MU_AT_FPS, status)
        return err

    def GetValue(self, vision_type, object_inf):

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

    def LedSetColor(self, led, det_color, undet_color, brightness):
        err, _ = self.__SendATandRead(
            MU_AT_LED, led, det_color, undet_color, brightness)
        return err

    def SensorSetDefault(self):
        err, _ = self.__SendATandRead(MU_AT_DEFAULT)
        return err

    def SetValue(self, vision_type, object_inf, value):
        return self.__write(vision_type, object_inf, value)

    def UartSetBaudrate(self, baud):
        err, _ = self.__SendATandRead(MU_AT_UARTBAUD, baud)
        return err

    def UpdateResult(self, vision_type, wait_all_result=True):
        vision_type_output = 0

        for vision_state in self.__vision_states:
            if vision_type & vision_state.vision_type:
                vision_id = 1 + \
                    self.__vision_types.index(vision_state.vision_type)
                state_select = self.__vision_states.index(vision_state)
                err, data = self.__SendATandRead(MU_AT_READ, vision_id, Status)

                if (not err) and data:
                    data = data.split(',')
                    frame = int(data[0][1:])
                    detect = int(data[1][1:])
                    if vision_state.frame != frame:
                        vision_state.frame = frame
                        vision_state.detect = detect

                        vision_state.detect = MU_MAX_RESULT if MU_MAX_RESULT < vision_state.detect else vision_state.detect
                        for i in range(vision_state.detect):
                            vision_state.vision_result[i].result_data1 = int(
                                data[2+i*5][1:])
                            vision_state.vision_result[i].result_data2 = int(
                                data[3+i*5][1:])
                            vision_state.vision_result[i].result_data3 = int(
                                data[4+i*5][1:])
                            vision_state.vision_result[i].result_data4 = int(
                                data[5+i*5][1:])
                            vision_state.vision_result[i].result_data5 = int(
                                data[6+i*5][1:])

                        self.__vision_states[state_select] = vision_state
                        vision_type_output = vision_type_output | vision_state.vision_type

        return vision_type_output

    def VisionBegin(self, vision_type):
        return self.VisionSetStatus(vision_type, "TRUE")

    def VisionEnd(self, vision_type):
        return self.VisionSetStatus(vision_type, "FALSE")

    def VisionSetDefault(self, vision_type):
        pass

    def VisionSetLevel(self, vision, level):
        err, _ = self.__SendATandRead(MU_AT_LEVEL, vision, level)
        return err

    def VisionSetStatus(self, vision_type, enable: bool):

        for vision_type_select in self.__vision_types:
            if vision_type_select & vision_type:
                vision_id = 1+self.__vision_types.index(vision_type_select)
                err, _ = self.__SendATandRead(MU_AT_VISION, vision_id, enable)
                if err:
                    return err

                if enable:
                    exists = False
                    for mv_vision_state in self.__vision_states:
                        if vision_type_select == mv_vision_state.vision_type:
                            exists = True
                            break
                    if not exists:
                        self.__vision_states.append(
                            MuVsVisionState(vision_type_select))
                else:
                    for mv_vision_state in self.__vision_states:
                        if vision_type_select == mv_vision_state.vision_type:
                            self.__vision_states.remove(mv_vision_state)
        return err

    def begin(self, uart):
        if "UART" == uart.__class__.__name__:
            self.__communication_port = uart
            # Setting serial port parameters
            self.__communication_port.init(timeout=1000, timeout_char=10)
            return self.SensorSetDefault()
        else:
            raise ValueError(
                "MuVisionSensor3AT begin %s cannot suppot!" % uart.__class__.__name__)

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

    def __write(self, vision, object_inf, data):
        if object_inf in [XValue, YValue, WidthValue, HeightValue, Label]:
            err, _ = self.__SendATandRead(
                MU_AT_WRITE, vision, object_inf, data)
            return err
        else:
            return MU_FAIL

    def WifiSetConfig(self, ssid, password, mode):
        self.__wifi_mode = mode
        err, _ = self.__SendATandRead(MU_AT_WIFISET, ssid, password, mode)
        return err

    def WifiGetConfig(self):
        _, res = self.__SendATandRead(MU_AT_WIFISET, MU_AT_QUERY)
        return res

    def WifiSetCon(self, status):
        err, _ = self.__SendATandRead(MU_AT_WIFICON, status, nowait=True)
        if err:
            return err
        count = 0
        while count < 15:
            res = self.__communication_port.readline()
            if res == MU_AT_OK_b:
                print("\nwifi connect succeed")
                return MU_OK
            elif res == MU_AT_ERROR_b:
                return MU_FAIL
            elif res == None:
                print("\rWaiting for WiFi connection:%ds" % count,end='')
                count += 1
            else:
                print(str(res, 'utf-8').replace('+WIFICON:','\n'), end='')

        self.Logger(LOG_INFO, "Wifi connecte TimeOut!")

        return MU_WRITE_TIMEOUT

    def WifiGetSIP(self):
        err, data = self.__SendATandRead(MU_AT_WIFISIP)
        if err:
            return err
        else:
            return data

    def WifiGetCIP(self):
        err, data = self.__SendATandRead(MU_AT_WIFICIP)
        if err:
            return err
        else:
            return data

    def WifiSetUDP(self, ip, port):
        err, _ = self.__SendATandRead(MU_AT_WIFIUDP, ip, port)
        return err

    def WifiGetUDP(self):
        _, res = self.__SendATandRead(MU_AT_WIFIUDP, MU_AT_QUERY)
        return res
