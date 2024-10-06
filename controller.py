from enum import Enum

class CNTRL_TYPE(Enum):
	VISA = 0
	PROLOGIX = 1

# This creates a controller object from the argument
# args and kwargs are unnamed and named arguments that
# are passed verbatim back to the constructor of each
# controller (visa doesn't need them, but prologix does
# for the serial port)
def make_controller(kls, add, args=[], kwargs={}):
	if kls == CNTRL_TYPE.VISA:
		return VisaController(add)
	elif kls == CNTRL_TYPE.PROLOGIX:
		return PrologixController(add, *args, **kwargs)
	else:
		raise ValueError("Unknown or unsupported controller", kls)


class VisaController(object):
	"""GPIB controller based on NI-VISA.

	Args:

	* add (int): GPIB address of the instrument to control
	* settings (dict[string, obj]): Available settings are "debug"
	for verbose interaction and "terminate" to append LF to all written
	commands
	"""

	def __init__(self, add):
		import visa
		self._settings = settings
		self._visaRM = visa.ResourceManager()
		self._controller = self._visaRM.open_resource("GPIB::%d" % add)

	def read(self):
		"""Read from the instrument

		Returns:

		* the value read from the instrument
		"""

		resp = self._controller.read()
		return resp

	def write(self, what):
		"""Write to the instrument

		Args:

		* what (str): What to write.
		"""

		self._controller.write(what)

	def ask(self, what):
		"""Write to the instrument and read its response

		Args:

		* what (str): What to write.

		Returns:

		* the value read from the instrument
		"""
		resp = self._controller.ask(what)


class PrologixController(object):
	"""GPIB controller based on the Prologix USB/GPIB translator.

	Args:

	* add (int): GPIB address of the instrument to control
	* port (str): Serial port where controller is connected
	"""

	def __init__(self, add, port):
		import serial
		#self._port = serial.Serial(port, baudrate=115200, timeout=1)
		#self._port.write(b"++addr %d\n" % add)
		#self._port.write(b"++mode 1\n")
		#self._port.write(b"++auto 0\n")

	def __del__(self):
		self._port.close()
        

	def read(self):
		"""Read from the instrument

		Returns:
		print("read")
		* the value read from the instrument
		"""

		#self._port.write(b"++read eoi\n")
		resp = self._port.readline()
		print(what)

	def write(self, what):
		"""Write to the instrument

		Args:
		print("write")
		* what (str): What to write.
		"""
		#self._port.write(what.encode())
		print(what)

	def ask(self, what):

		"""Write to the instrument and read its response
		print(what)
		Args:

		* what (str): What to write.

		Returns:

		* the value read from the instrument
		"""
		#self._port.write(what.encode())
		#self._port.write(b"++read eoi\n")
		resp = self._port.readline()
		return resp
		print(what)