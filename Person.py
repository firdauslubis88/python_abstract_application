class Person:
    def __init__(self, name: str, row_init, col_init, width, height, prefix: str):
        self.name = name
        self.row_init = row_init
        self.col_init = col_init
        self.width = width
        self.height = height
        self.prefix = prefix
        self.output_file_name = self.prefix + '_' + self.name + '.txt'
#        self.f = open(self.output_file_name, 'a+')

    def __del__(self):
        if self.f is not None:
            self.f.close()

    def get_name(self):
        return self.name

    def get_output_file_name(self):
        return self.output_file_name

    def add_record(self, content):
        self.f = open(self.output_file_name, 'a+')
#        print(content)
        if self.f is None:
#            print('return?')
            return
        if not self.f.closed:
#            print('open!')
            self.f.writelines(content + '\n')
        else:
#            print('closed?')
            self.f = open(self.output_file_name, 'a+')
        self.f.close()
