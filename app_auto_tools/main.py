from case.test_H7148 import TestH7148


class Main:

    def test_h7148(self, test_count):
        
        config_path = "./config/config.ini"
        test_case= TestH7148(config_path)

        test_case.test_app_connect()


if __name__ == '__main__':

    main = Main()
    main.test_h7148(5000)

