import os
import time  # Various operations with time (pauses)
import RPi.GPIO as GPIO  # It can only be used when attaching the E or RS signal to the GPIO in RasPi


class Lcd:
    def __init__(self, s_data_pin, s_clk_pin, reset_pin) -> None:
        self.s_data_pin = s_data_pin
        self.s_clk_pin = s_clk_pin
        self.reset_pin = reset_pin
        self.font2 = {}
        self.txtmapa = {}
        self._init()
        self.clear()
        self._init_text_mode()

    def clear(self, pattern=0):
        self._clear_text()

    def _clear_text(self):
        self._send_byte(0, 0b00110000)  # function set (8 bit)
        self._send_byte(0, 0b00110000)  # function set (basic instruction set)
        self._send_byte(0, 0b00001100)  # displ.=ON , cursor=OFF , blink=OFF
        self._send_byte(0, 0b00000001)  # clear
        self.txtmapa[0] = "                "
        self.txtmapa[1] = "                "
        self.txtmapa[2] = "                "
        self.txtmapa[3] = "                "

    def _init_text_mode(self):
        self._send_byte(0, 0b00110000)
        self._send_byte(0, 0b00110100)
        self._send_byte(0, 0b00110110)
        self._send_byte(0, 0b00000010)
        self._send_byte(0, 0b00110000)
        self._send_byte(0, 0b00001100)
        self._send_byte(0, 0b10000000)

    def _quickSleep(self):
        time.sleep(0)

    def _set_data_pin(self, bit):

        if bit:
            GPIO.output(self.s_data_pin, True)
        else:
            GPIO.output(self.s_data_pin, False)

    def _strobe5(self):
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)

    def _strobe(self):
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)

    def _strobe4(self):
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, True)
        self._quickSleep()
        GPIO.output(self.s_clk_pin, False)

    def display_text(self, string, column, row):

        if len(string) + column > 16:  # If the line is longer than 16 characters,
            string = string[0 : 16 - column]  # ... so the end is cut off

        self._set_text_cursor_pos(
            column, row
        )  # The start position of the text is sent to the display
        for printCharGraphicMode in range(len(string)):
            self._send_byte(
                1, ord(string[printCharGraphicMode : printCharGraphicMode + 1])
            )  # Characters from the text are gradually streaked into the display
            pomtext = (
                self.txtmapa[row][: column + printCharGraphicMode]
                + string[printCharGraphicMode : printCharGraphicMode + 1]
                + self.txtmapa[row][column + printCharGraphicMode + 1 :]
            )
            self.txtmapa[row] = pomtext  # Memory for text mode

    def _set_text_cursor_pos(self, column, row):
        shift = column
        if row == 1:
            shift = column + 32
        if row == 2:
            shift = column + 16
        if row == 3:
            shift = column + 48

        self._send_byte(
            0, 0b10000000 + int(shift / 2)
        )  # Address Counter na pozadovanou pozici

        # In the case of --lichen-- columns, the printCharGraphicMode must be filled in with the printCharGraphicMode on the display before the new printout
        if column / 2.0 != column / 2:
            orignal_predcharacter = self.txtmapa[row][
                column - 1 : column
            ]  # "Predcharacter" is determined from the auxiliary text memory
            self._send_byte(1, ord(orignal_predcharacter))

    def _send_byte(self, rs, byte):

        self._set_data_pin(
            1
        )  # the beginning of the communication is done with the "synchro" sequence of 5 singles
        self._strobe5()

        self._set_data_pin(0)  # Then the RW bit is sent (when set to "0")
        self._strobe()
        self._set_data_pin(rs)  # Then send the RS bit (commands = "0"; data = "1")
        self._strobe()
        self._set_data_pin(0)  # Followed by zero bit
        self._strobe()

        for i in range(7, 3, -1):  # And then up four bits of the sent byte
            self._set_data_pin(byte & (1 << i))
            self._strobe()

        self._set_data_pin(0)  # Then the separation sequence is sent 4x "0"
        self._strobe4()

        for i in range(
            3, -1, -1
        ):  # Followed by the rest of the data (the bottom 4 bits of the sent byte)
            self._set_data_pin(byte & (1 << i))
            self._strobe()

        self._set_data_pin(0)  # To restart the separation sequence 4x "0"
        self._strobe4()

    # HW initial setting + reset the display
    def _init(self):
        # GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.s_data_pin, GPIO.OUT)  # (pin 26 = GPIO7)   = DATA
        GPIO.setup(self.s_clk_pin, GPIO.OUT)  # (pin 24 = GPIO8)   = CLOCK
        GPIO.setup(self.reset_pin, GPIO.OUT)  # (pin 22 = GPIO25)  = RESET

        GPIO.output(self.s_data_pin, False)  # DATA to "0"
        GPIO.output(self.s_clk_pin, False)  # CLOCK to "0"
        GPIO.output(self.reset_pin, False)  # RESET to "0"
        time.sleep(0.1)
        GPIO.output(self.reset_pin, True)  # RESET to "1"
        self._loadTextFont("font2.txt")  # Retrieve an external font from the file

    def _loadTextFont(self, fileName):

        script_path = os.path.abspath(__file__)  # i.e. /path/to/dir/foobar.py
        script_dir = os.path.split(script_path)[0]  # i.e. /path/to/dir/
        fullPathFileName = os.path.join(script_dir, fileName)

        fontfile = open(fullPathFileName, "r")
        adresafontu = 0
        for row in fontfile:
            rozlozeno = row.split(
                ","
            )  # Saturation of individual bytes from one line ...
            for byte in range(8):  # 8 byte on one row in a file
                self.font2[adresafontu] = int(
                    rozlozeno[byte][-4:], 0
                )  # ... and save everyone on the list
                adresafontu = adresafontu + 1
        fontfile.close()


# def main():

#     init()              # Basic HW system setup - port directions on the expander and reset the display
#     clearDisplay(0)     # Complete deletion of the display


# #==============================================================
# #              Starts the default examples
# #==============================================================


# #- - - - - - - - - Writing text to the display - - - - - - - - - - - - - - - - - - - -
#     initTextMode()     # Switch to text mode

#     printStringTextMode("NU BLJA,",0,0)   # Display the text in the text mode at specified coordinates
#     printStringTextMode("TAK TO",0,1)
#     printStringTextMode("PO PIZZHE",0,2)
#     printStringTextMode("BUDET!!!",0,3)


#     exit(0)
