import re


def extract_data(file_path, timestamp_pattern):
	with open(file_path, 'r') as file:
		content = file.read()
	return re.split(f'({timestamp_pattern})', content)[1:]


def create_block_list(data):
	return [(data[i], data[i+1]) for i in range(0, len(data), 2)]


def parse_block_list(data, header=False, delim=None):
	parsed_list = []
	for timestamp, table in data:
		lines = table.strip().split('\n')
		headers = lines[0].split() if header else None
		processes = lines[1:] if header else lines
		table_data = []
		for process in processes:
			if header:
				process_data = {header: value for header, value in zip(headers, process.split(delim))}
				table_data.append(process_data)
			else:
				table_data.append(process.split(delim))
		parsed_list.append((timestamp, table_data))
	return parsed_list



