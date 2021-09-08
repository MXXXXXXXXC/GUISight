"""
Record coverage in linux
"""
import os
import _thread


class EmmaHelper:
    def __init__(self, java_class_path, main_class, report_type='txt', merge=False, jar_file = None):
        if jar_file:
            print("Jar file")
            if not os.path.exists(jar_file):
                print('Java File not found')
                exit(0)
        else:
            if not os.path.exists(java_class_path+'/'+main_class+'.class'):
                print('Java File not found')
                exit(0)
        self.jar_file = jar_file
        self.java_class_path = java_class_path
        self.main_class = main_class
        self.report_type = report_type
        self.merge = merge

    def open_application(self):
        _thread.start_new_thread(self.on_the_fly_test, ())

    def on_the_fly_test(self):

        if self.merge:
            # Java 1.8.0
            if self.jar_file:
                command = 'java -noverify -cp ./emma.jar emmarun -r %s -raw -merge y -jar %s' % (self.report_type, self.jar_file)
            else:
                command = 'java -noverify -cp ./emma.jar emmarun -r %s -raw -cp %s %s -merge y' % (self.report_type, self.java_class_path,  self.main_class)
        else:
            if self.jar_file:
                command = 'java -noverify -cp ./emma.jar emmarun -jar %s' % (self.jar_file)
            else:
                command = 'java -noverify -cp ./emma.jar emmarun -cp %s %s' % (self.java_class_path,  self.main_class)

        os.system(command)

    def merge_report(self):
        if self.merge:
            if not os.path.exists('./coverage.es'):
                print('Report File not found')
                return
            command = 'java -noverify -cp ./emma.jar emma report -r %s -in ./coverage.es' % (self.report_type)
            os.system(command)

    @staticmethod
    def remove_report():
        if os.path.exists('./coverage.es'):
            command = 'rm coverage.es'
            os.system(command)

    def show_report(self):
        if os.path.exists('./coverage.%s' % self.report_type):
            with open('./coverage.%s' % self.report_type) as report:
                for line in report.readlines():
                    print(line)

    @staticmethod
    def stop_application():
        os.system("""ps -ef | grep emm[a]run | awk '{print $2}' | xargs kill""")
