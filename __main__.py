import sys, os, datetime, shutil


date_format = '%G-W%V/%u'


def log(msg, *args):
	if len(args) > 0:
		msg = msg % args
	
	print(msg, file = sys.stderr)


def read_file(path):
	with open(path, 'rb') as file:
		return file.read()


def makedirs(path):
	if not os.path.exists(path):
		log('Creating %s', path)
		os.makedirs(path)


def rename(source_path, target_path):
	if target_path == source_path:
		return
	
	if os.path.exists(target_path):
		log('File %s exists, comparing with %s ...', target_path, source_path)
		
		assert read_file(source_path) == read_file(target_path), 'File already exists: {}'.format(target_path)
	
	log('Moving %s to %s', source_path, target_path)
	os.rename(source_path, target_path)


def rmtree(path):
	log('Removing %s', path)
	shutil.rmtree(path)


def main(dir):
	def unsort_images():
		for dirpath, dirnames, filenames in os.walk(dir):
			for i in filenames:
				_, ext = os.path.splitext(i)
				
				if ext in ['.jpg', '.png', '.mov']:
					yield os.path.join(dirpath, i)
	
	def is_empty(dir):
		return os.path.exists(dir) and all(i.startswith('.') for i in os.listdir(dir))
	
	def dir_for_date(date):
		return os.path.join(dir, date.strftime(date_format))
	
	check_empty_dirs = []
	
	for i in unsort_images():
		file_dir, file_name = os.path.split(i)
		name_part, _ = os.path.splitext(file_name)
		date_part = ' '.join('-'.join(name_part.split('-')[:3]).split(' ')[:2])
		date = datetime.datetime.strptime(date_part, '%Y-%m-%d %H.%M.%S')
		new_path = os.path.join(dir_for_date(date), file_name)
		
		makedirs(os.path.dirname(new_path))
		rename(i, new_path)
		check_empty_dirs.append(file_dir)
	
	while check_empty_dirs:
		empty_dirs = check_empty_dirs
		check_empty_dirs = []
		
		for i in empty_dirs:
			if is_empty(i):
				rmtree(i)
				check_empty_dirs.append(os.path.dirname(i))


try:
	main(*sys.argv[1:])
except KeyboardInterrupt:
	log('Operation interrupted.')
