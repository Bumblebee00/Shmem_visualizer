import os
from struct import unpack
from time import sleep

# num_type should be:
# 'f' for floats
# 'i' for ints
# 'd' for double
def analyze_num(path, num_type, num_name, precision):
	info = ''
	try:
		content = open(SHMEM_handle_dir+path, 'rb').read()
	except FileNotFoundError:
		print(f'ERROR: file {path} not found !!!!')
	size = int(len(content)/4)
	info += f'{path} contains {size} {num_name}\n'
	if precision=='fast':
		info += f"First three: {[unpack(num_type, content[i*4:(i+1)*4])[0] for i in range(3)]}\n"
		info += f"Last three: {[unpack(num_type, content[i*4:(i+1)*4])[0] for i in range(size-3,size)]}\n"
	elif precision=='slow':
		numbers = [unpack(num_type, content[i*4:(i+1)*4])[0] for i in range(size)]
		info += f"First three: {numbers[:3]}\n"
		info += f"Last three: {numbers[size-3:size]}\n"
		mean = sum(numbers)/size
		variance = sum((i - mean) ** 2 for i in numbers) / size
		info += f"Mean: {mean}\n"
		info += f"Variance (=distance from mean): {variance}\n"
		info += f"Max: {max(numbers)}\n"
		info += f"Min: {min(numbers)}\n"
	return info

def analyze_floats(path, precision):
	return analyze_num(path, 'f', 'floats', precision)

def analyze_ints(path, precision):
	return analyze_num(path, 'i', 'ints', precision)


def analyze_chars(path, precision):
	info = ''
	try:
		content = open(SHMEM_handle_dir+path, 'rb').read()
	except FileNotFoundError:
		print(f'ERROR: file {path} not found !!!!')
	size = len(content)
	info += f'{path} contains {size} chars\n'
	if precision=='fast':
		info += f"First three: {content[:3]}\n"
		info += f"Last three: {content[size-3:size]}\n"
	elif precision=='slow':
		info += 'Here they are: '+content.decode()+'\n'
		info += 'Did I found ARD1T0 in those chars? '
		if b'ARD1T0' in content: info += 'Yes!!!'
		else: info += 'No:(...'
	return info+'\n'

data_types_functions = {'float':analyze_floats, 'int':analyze_ints, 'char': analyze_chars}

# General variables
frequency = 1 # Hertz
SHMEM_handle_dir = '/dev/shm/'
SHMEM_handle_start = 'DIANA_SHMEM'

# Asks which SHMEM objects to trace
SHMEM_handle_paths = list(filter(lambda x: x.startswith(SHMEM_handle_start),os.listdir(SHMEM_handle_dir)))
print(f'I found {len(SHMEM_handle_paths)} SHMEM handle files: ',*SHMEM_handle_paths,'\n')
print(f"Now i will ask you for each SHMEM object if you want to trace it or not, if yes you should input the type (int, float or char) and the precision (fast or slow, if omitted i assume fast), otherwise input 'no'. If 'float slow' is too long for you you can input 'f s', same for 'no' and 'n', 'int fast' and 'i f' ecc...\n")
to_trace = {}
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

#Traces the SHMEM objects
i=0
d=-1
while True:
	print()
	for path, info in to_trace.items():
		# info[0] is data type info[1] is precision
		info = data_types_functions[info[0]](path, info[1])
		print(info)
	# fancy print
	tl=os.get_terminal_size().columns
	sep = '-'*(tl-1)
	print(sep[:i]+'o'+sep[i:])
	if i==0 or i==tl-1: d*=-1
	i+=d
	#
	sleep(1/frequency)