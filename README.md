# esp32-micropython

After cloning the foloowing repo which provides MicroPython for ESP32, with 4MB psRAM support and esp-idf building system, we can build and flash the firmware to the board.
[https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo](https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo)


#### Enable SPIFFS

	cd ~/MicroPython_ESP32_psRAM_LoBo/MicroPython_BUILD
	sudo apt-get install libncurses-dev ncurses-dev flex bison gperf
	./BUILD.sh menuconfig
	
menuconfig → MicroPython → File systems → Use SPIFFS

#### Build the Micropython firmware and flash it to the board
	./BUILD.sh -j4
	./BUILD.sh flash

#### Make the file system
	./BUILD.sh makefs
#### Serial port permissions
https://askubuntu.com/questions/112568/how-do-i-allow-a-non-default-user-to-use-serial-device-ttyusb0


