import os
import struct
from time import sleep

# num_type should be:
# 'f' for floats
# 'i' for ints
# 'd' for double
def analyze_num(path, num_type, precision):
	info = ''
	content = open(SHMEM_handle_dir+path, 'rb').read()
	size = int(len(content)/4)
	info += f'{path} contains {size} floats\n'
	if precision=='fast':
		info += f"First three: {[struct.unpack(num_type, content[i*4:(i+1)*4])[0] for i in range(3)]}\n"
		info += f"Last three: {[struct.unpack(num_type, content[i*4:(i+1)*4])[0] for i in range(size-3,size)]}\n"
	elif precision=='slow':
		floats = [struct.unpack(num_type, content[i*4:(i+1)*4])[0] for i in range(size)]
		info += f"First three: {floats[:3]}\n"
		info += f"Last three: {floats[size-3:size]}\n"
		mean = sum(floats)/size
		variance = sum((i - mean) ** 2 for i in floats) / size
		info += f"Mean: {mean}\n"
		info += f"Variance (=distance from mean): {variance}\n"
		info += f"Max: {max(floats)}\n"
		info += f"Min: {min(floats)}\n"
	return info

def analyze_floats(path, precision = 'fast'):
	return analyze_num(path, 'f', precision)

def analyze_ints(path):
	return analyze_num(path, 'i', precision)


def analyze_chars(path):
	info = ''
	file = open(SHMEM_handle_dir+path, 'rb')
	content = file.read()
	info += f'{path} contains {len(content)} chars\n'
	info += 'They are beautiful\n'
	return info

data_types_functions = {'float':analyze_floats, 'int':analyze_ints, 'char': analyze_chars}

SHMEM_handle_dir = '/dev/shm/'
SHMEM_handle_start = 'DIANA_SHMEM'
SHMEM_handle_paths = list(filter(lambda x: x.startswith(SHMEM_handle_start),os.listdir(SHMEM_handle_dir)))
print(f'I found {len(SHMEM_handle_paths)} SHMEM handle files: ',*SHMEM_handle_paths,'\n')
print(f"Now i will ask you for each file if you want to trace it or not, if yes you should input the type (int, float or char) and the precision (fast or slow, if omitted i assume fast), otherwise input 'no'. If 'float slow' is too long for you you can input 'f s', same for 'no' and 'n', 'int fast' and 'i f' ecc...\n")
to_trace = {}
# asks which paths to trace
for path in SHMEM_handle_paths:
	print(f'You want to trace {path}?')
	valid_answ = False
	while not valid_answ:
		decision = input('>')
		valid_answ = True
		decision = decision.lower().split()
		if decision[0] in ['int', 'i']: to_trace[path] = ['int']
		elif decision[0] in ['float', 'f']: to_trace[path] = ['float']
		elif decision[0] in ['char', 'c']: to_trace[path] = ['char']
		elif decision[0] in ['no','n']: continue
		else:
			print(f'Bad type input, try again')
			valid_answ = False
			continue
		if len(decision)==1 or decision[1] in ['fast','f']: to_trace[path].append('fast')
		elif decision[1] in ['slow','s']: to_trace[path].append('slow')
		else:
			print(f'Bad precision input, try again')
			valid_answ = False

run = True
while run:
	for path, info in to_trace.items():
		# info[0] is data type info[1] is precision
		info = data_types_functions[info[0]](path, info[1])
		print(info)
	print('-'*os.get_terminal_size().columns)
	sleep(2)
