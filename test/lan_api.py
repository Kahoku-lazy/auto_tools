# coding=UTF-8
import base64
import time
import socket
import json
import base64
import binascii

# 组播组IP和端口
## ucast_dev_ip = '192.168.50.117'
ucast_dev_port = 4003
mcast_group_ip = '239.255.255.250'
mcast_group_port = 4001


class ApiTest():
    # 组播扫描
    def sender(self):
        # 建立发送socket，和正常UDP数据包没区别
        socket.setdefaulttimeout(60)
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.local_addr = ('', 4002)
        self.send_sock.bind(self.local_addr)
        cmd_json = {
            "msg": {
                "cmd": "scan",
                "data": {
                    "account_topic": "GA/123456789"
                }
            }
        }
        message = json.dumps(cmd_json)
        self.send_sock.sendto(message.encode(), (mcast_group_ip, mcast_group_port))
        print("**************扫描设备IP**************\r\n")
        try:
            recv_data = self.send_sock.recvfrom(1024)
            recv_msg = recv_data[0]  # 设备信息
            send_addr = recv_data[1]  # ip地址
            print("%s:%s\r\n" % (str(send_addr), recv_msg.decode("gbk")))
            ucast_dev_ip = send_addr[0]
            t.send_param(ucast_dev_ip)
        except Exception as e:
            print(e)
        time.sleep(2)

    # 单播控制
    def send_param(self, ip):
        count = 0
        # ucast_dev_ip = '192.168.50.117'
        # ucast_dev_port = 4003
        print("扫描到的ip地址：：：", ip)

        # 查询设备
        cmd_json = {
            "msg": {
                "cmd": "devStatus",
                "data": {
                }
            }
        }
        message = json.dumps(cmd_json)
        self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        try:
            recv_data_dev = self.send_sock.recvfrom(1024)
            recv_msg = recv_data_dev[0]
            send_addr = recv_data_dev[1]
            print("%s:%s\r\n" % (str(send_addr), recv_msg.decode("gbk")))
        except Exception as e:
            print(e)
        time.sleep(5)

        """
        打开单个ic开关
        """
        hex_str_on = 'bb0006b1010D'  # uwANsAEC/wAAAP8ABQ==
        binary_data_on = binascii.unhexlify(hex_str_on)
        base64_str_on = base64.b64encode(binary_data_on).decode('utf-8')
        cmd_json_on = {
            "msg": {
                "cmd": "razer",
                "data": {
                    "pt": base64_str_on
                }
            }
        }
        message_on = json.dumps(cmd_json_on)
        self.send_sock.sendto(message_on.encode(), (ip, ucast_dev_port))

        while True:  # 循环次数
            # 给定的十六进制字符串
            # 10 ic
            # hex_str ='bb0025b0000aff000000ff000000ffff000000ff000000ffff000000ff000000ffff000024'
            # hex_str_1 ='bb001eb0000a53cec3329ae6c81471404301d83fc9d921176c3ab2b765da678c66049b930c'
            # 100
            # hex_str =   'bb0133b00064ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff00005D'
            # hex_str_1 = 'bb0133b00064b6808e3b0cb24fd66a6632d8ec1a2ca376e0dc4cc8eb0ed468df918a34fc15068d893acfe58466f642314475d87c945baf03b26c155ec63a75979eb772f133182f49bec12502fd47765754e29772279246cf2ca9ee0c8078dc9cb67583bf26ba5af59467398022cae92daef4ac14f60807051dd9cb9bf119d6cf6a0e7e7403c736ad7e2ef326d9b5a81cee4b03a46c80beaf6fe9a24055897811765d3d43711b04b89eeda3744d55b257478ed3a5ecb08bbb4b0b90c1919580e7e7a0481b7875e9e0081a6d44ac48150f83fbc10c9318e22400429da238d5cafc03831fdbd7d58e96bbfa0817a392abb08a3c1a530313903e58177e7e47077db1df93f9d1fd7642bb196be93cc7b426368aabfadd4191f1ec022c7f8f963c9ddb94ddbb5351df947eb3dbbcda4a5a4f7daab562'
            # 160
            # hex_str = 'bb01e7b000a0ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ff4D'   # uwANsAEC/wAAAP8ABQ==  160
            # hex_str_1 = 'bb01eab000a12e8d030c557a96b57ebd4ef88f4cf585b08aea9ea512e10791c2aa8919bc6d508ef5f16a11bb972178e9008de0ed047d01141620384e6bc24f6c53e887e6b2366a7affd79c1423de48e92fb62ba58dac3d45dc982974f28c70443ff8345c39ab575b2d3efcd2c6803763075549e8e913ce835a72198cf17dd98ef426310b6bbe8a204a00ac5d672a8aee740bfdf80c2b11e9567bcb9c4730c5a1e388fac147de6b5a4afe295c05455db9889660d1c04d83eac675ffd4d8a14c0be1559090442892d4a9d64f898acb25fd7dd9cccda6fb3d6e8cac71c8f81c5c87c80e59fb8f5a83f3854e12fe82ec0338f4afcd2e718bba9eb42d609b3adcdcd6c311d59e3d02d0fad60e03d99a93c3f5d6cfa473aaf0b0c1d17c89856828ecb87c6f8377baa8763922e7635b4e27b95f2ec6655862bf7a73e49dc5f841aa776d0fd9a0fa809285f32e0e50928c692ca111411750a8fde6eb26725686d94a82e22381bd2f58162883f03028bf0b93a459b5fe804bec5fd3a59116fbb6defbe1ab290a4f84bff4a6f7c8ee620adeec8348549a72e98a4b6ec0ae9f32ac626efc35eb9226d5f21a0d85fec6f3b9987e233d869554919187a7b88d6c669ad86213e51c3cdf8cf8c0b05815f853d44c72e1847427652538c89361b19ae393ea7f91b5ea40a775e909478e144E'  # 161
            # 150
            # hex_str = 'bb01c9b00096ff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ff55'   # uwANsAEC/wAAAP8ABQ==  150
            # 170
            # hex_str = 'bb0205b000aaff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffA6'   # uwANsAEC/wAAAP8ABQ==
            # 20
            # hex_str = 'bb0043b00014ff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff000000ffff000000ff005c'
            # hex_str_1 = 'bb0043b000141114a26e759684770d93b8cc7a6e40b651cdea0cbc1f2e0a171aaabebb34492c399a263178ac5ea1e0c45c8897e78e31c5d6e230405235c38a13319f31'
            # 200
            # hex_str = 'bb025fb000c8ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff0000ff000000ff000000ffff000000ff000000ffff000000ff000000ffff00009E'     # 200
            # 165
            # hex_str_1 = 'bb01c4b000a5eeb8e5cc326ef8c8756182a12862bb71cd11a6c6911bae2eb87289f672a61ae1fd4f74b6ab1eceee41eda662d56bd7f7b842996388b8fa25e60869464303089a79a5752a029dd2c390fdfa2e27360f75ffb3db43112936462bf555aba1a42c80a2ef7e944b44fb9c04c17bda28a77935c1a5431a730bc6d8d035cfd5fbfc57062dbf36fe5febffd0cf3a0ddc16758776a0b6707d16b4e3e64921ff806422d5a7bf60c2b0be2c94c8fecceecf9922eb56ba72d4c8d0e33ad34bffc1f4b52c7f5ca37234eb25ee95975b6f4c7bececbe7b6c300de22e85d420365542492f3520882e8ece486c9061df00068174e59c2a4c11022eb040120d4834845cdf3a0655903ff688180462f458f2689d619ff8c90a2154cbcfe799489ba1dd725ea61a9fe56ff8ba6a2bb4751dc16d7b4da070265858ec129d75f79fceded7a8609f2a3c0ded4325bb1ac47e98740ef821524fab508ec26fdab3e3e6467bee4d2152c31e4c873e7e3fa0191ff4299f81a392b246732bbe38a81a14f3c9f8c5b062b224bde009339cc544e57cc12444d0b2d48e6301599de7fb6be0392eb5f3387f9331bc53bee8df8e89d28464983c22dc58b5c57d583585ef2e048a9eb7df0f5cc8a73153f9e170f6dd3fb92a78669060c92867cbc3bb2d68c1305f3daae13f0b919c375caf292d47c7fda69e947c2ff284ba9411'
            # 162
            # hex_str = 'bb01edb000a2d5542d7772498382a00dd5e468c3f1a859ec749888a83f7b7bb678d04609349ad713c97614c38974efc68ed225c99c68d82918580d67193020a73602093c1a11bd4517f90ab74c48bfbb06aa5b170cf0d3e165fe2ff1cd0843f1913dcc23b971ce267695158cb44108f1c3cc54f6a579ba7a41fab805476e3b63df26b53255ce26524bde2ede567352dec011e86f7fc1ad5b7a01dfbfae756094a2ebb59a3dceeb17634bc5a263eaf8aded8d5fd4ec64cd745fa07ca24479c4b2a6b173fd1edd56bc41924e1fab37bed039fb944e192d14a9e92a467720af196f4e61333192240ce2e5b1fb7ad1876161e2fac2de6c126a97b44e5a035720fa3fed672f34b93f76921273c13d53f0792013df35234aa3edbab3901d7a7240c854748badc8961b0fab1b0ad3a44907f4c76e643ef791a68708ffa5e4d6b13c3dcc090b679874085b06ccd00fa2a448540b5050ec8c3c240cb4053587d592be02f508d352bb0836e6024d1de51c877e29e4281cb17f3151f84a6dbb1de01408d56278d36c0c142a14be3bc4213aafaaa4c7ba3fe3019779ac0ad312e5882f9c3bdba99d7d53c158c7749f853505681512b76e23cf3dd3ab01cd1e20f19cb0e6d6ce650ec82488d81a60f2d263a225cca64dc174fef74cbc3c83677d0805429865ac5536817867cc83ba0aed0dfa8C'     # 162

            # 将十六进制字符串转换为字节数据
            binary_data = binascii.unhexlify(hex_str)

            binary_data_1 = binascii.unhexlify(hex_str_1)
            # print(binary_data)
            # 将字节数据编码为 Base64 格式
            base64_str = base64.b64encode(binary_data).decode('utf-8')
            base64_str_1 = base64.b64encode(binary_data_1).decode('utf-8')
            # print(base64_str)
            cmd_json = {
                "msg": {
                    "cmd": "razer",
                    "data": {
                        "pt": base64_str
                    }
                }
            }
            cmd_json_1 = {
                "msg": {
                    "cmd": "razer",
                    "data": {
                        "pt": base64_str_1
                    }
                }
            }
            # print(cmd_json)
            message = json.dumps(cmd_json)
            message_1 = json.dumps(cmd_json_1)
            print(message)

            self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
            time.sleep(0.1)    # 间隔时间两个都要改 1 = 1000ms
            self.send_sock.sendto(message_1.encode(), (ip, ucast_dev_port))
            time.sleep(0.1)    # 间隔时间

            # # 开机
            # cmd_json = {
            #     "msg": {
            #         "cmd": "turn",
            #         "data": {
            #             "value": 1
            #         }
            #     }
            # }
            # message = json.dumps(cmd_json)
            # self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
            # print("turn on\r\n")
            # time.sleep(2)

        # 关机

        # while count < 100:  # 循环次数
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "turn",
        #             "data": {
        #                 "value": 0
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("turn off\r\n")
        #     time.sleep(2)
        #
        #     # 开机
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "turn",
        #             "data": {
        #                 "value": 1
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("turn on\r\n")
        #     time.sleep(2)
        #
        #     # 亮度
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "brightness",
        #             "data": {
        #                 "value": 50
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("set brightness 50\r\n")
        #     time.sleep(2)
        #
        #     # 亮度
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "brightness",
        #             "data": {
        #                 "value": 100
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("set brightness 100\r\n")
        #     time.sleep(2)
        #
        #     # 颜色
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "colorwc",
        #             "data": {
        #                 "color": {
        #                     "r": 255,
        #                     "g": 0,
        #                     "b": 0
        #                 }
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("set red\r\n")
        #     time.sleep(2)
        #
        #     # 颜色
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "colorwc",
        #             "data": {
        #                 "color": {
        #                     "r": 0,
        #                     "g": 255,
        #                     "b": 0
        #                 }
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("set green\r\n")
        #     time.sleep(2)
        #
        #     # 颜色
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "colorwc",
        #             "data": {
        #                 "color": {
        #                     "r": 0,
        #                     "g": 0,
        #                     "b": 255
        #                 }
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("set blue\r\n")
        #     time.sleep(2)
        #
        #     # 色温
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "colorwc",
        #             "data": {
        #                 "colorTemInKelvin": 7000
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("set cw 7000\r\n")
        #     time.sleep(2)
        #
        #     # 色温
        #     cmd_json = {
        #         "msg": {
        #             "cmd": "colorwc",
        #             "data": {
        #                 "color": {"r": 255, "g": 185, "b": 105},
        #                 "colorTemInKelvin": 3000
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("set cw 3000\r\n")
        #     time.sleep(5)
        #
        #     cmd_json1 = {
        #         "msg": {
        #             "cmd": "devStatus",
        #             "data": {
        #             }
        #         }
        #     }
        #     message = json.dumps(cmd_json1)
        #     self.send_sock.sendto(message.encode(), (ip, ucast_dev_port))
        #     print("get status\r\n")
        #     try:
        #         recv_data_status = self.send_sock.recvfrom(1024)
        #         recv_msg = recv_data_status[0]
        #         send_addr = recv_data_status[1]
        #         print("%s:%s\r\n" % (str(send_addr), recv_msg.decode("gbk")))
        #     except Exception as e:
        #         print(e)
        #     time.sleep(2)
        #     count += 1
        #     print("**************第{}次测试完成**************".format(count))


if __name__ == "__main__":
    t = ApiTest()
    t.sender()
    # t.send_param()
