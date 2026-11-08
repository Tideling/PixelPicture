from PIL import Image
import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import random

image_path = None
pixel = 1
mis = 50
img_name = ""
img_weight = 0
user_name = os.environ.get('USERPROFILE')

class FrontEnd():
    def __init__(self, creator = None):
        if creator == None:
            global image_path
            # 创建主窗口
            root = tk.Tk()
            root.title("像素方块的硬核才是王道")
            root.geometry("400x300")
            root.resizable(False, False)

            # 选择路径按钮
            select_button = tk.Button(root, text="选择目标图片", fg="#ffffff", font=("TkDefaultFont", -18, "bold"), width=15, height=3, bg="#cdac06", command=lambda: self.select_pic())
            select_button.place(relx=0.5, y=20, anchor="n")

            # 路径显示
            self.path_txt = tk.Label(root, text="???", fg="#FFFFFF", bg="#555555", font=("TkDefaultFont", -20), anchor="center", wraplength=300)
            self.path_txt.place(relx=0.5, y=250, anchor="n")

            # 提示显示
            self.hint_txt = tk.Label(root, text="", fg="#FF0000", font=("TkDefaultFont", -12), anchor="center", wraplength=300)
            self.hint_txt.place(relx=0.5, y=230, anchor="n")

            # 像素大小
            self.scale_txt = tk.Label(root, text="像素大小(不建议过高)", fg="#000000", font=("TkDefaultFont", -16), anchor="center")
            self.scale_txt.place_forget()

            self.scale = ttk.Combobox(root, width=10, height=6, values=[], state="readonly")
            self.scale.place_forget()

            # 色差阈值大小
            mis_txt = tk.Label(root, text="色差阈值", fg="#000000", font=("TkDefaultFont", -16), anchor="center")
            mis_txt.place(relx=0.35, y=120, anchor="n")

            mis = tk.Scale(root, from_=10, to=80, resolution=1, width=15, orient="horizontal", command=lambda v: self.set_mis(int(float(v))))
            self.scale.bind("<<ComboboxSelected>>", self.set_pixel)
            mis.place(relx=0.6, y=100, anchor="n")

            # 开始转换按钮
            self.select_button = tk.Button(root, text="开始转换", fg="#ffffff", font=("TkDefaultFont", -13), width=7, height=1, bg="#0d18e2", command=lambda: self.start())
            self.select_button.place_forget()

            root.mainloop()

    def hint(self, hint, color = "#000000"):
        self.hint_txt.config(text=hint, fg=color)
        # print(hint)

    def set_pixel(self, event=None):
        global pixel
        value = self.scale.get()
        pixel = int(value)

    def set_mis(self, value):
        global mis
        mis = value

    def select_pic(self):
        def divisors(num):      # 计算能整除像素的数
            divisors = []
            for i in range(1, num + 1):
                if num % i == 0:
                    divisors.append(i)
            return divisors
        
        global image_path
        global img_name
        global img_weight

        image_temp = filedialog.askopenfilename(filetypes=[(r"png/jpg图像选择", "*.jpg *.jpeg *.png")])
        try:
            with Image.open(image_temp) as img:     # 判断图像是否为正方形
                if img.size[0] == img.size[1]:
                    self.path_txt.config(text=f"{image_temp.split("/")[-1]}")
                    self.hint("", "#FF0000")
                    img_name = f"{image_temp.split("/")[-1]}"
                    image_path = image_temp
                    img_weight = img.size[0]

                    self.select_button.place(relx=0.5, y=190, anchor="n")
                    self.scale.config(values=divisors(img.size[0]))
                    self.scale.set(1)
                    self.scale.place(relx=0.6, y=160, anchor="n")
                    self.scale_txt.place(relx=0.24, y=160, anchor="n")

                    print(image_path)
                else:
                    self.hint("错误，图像长宽比必须为1:1", "#FF0000")
                    self.scale.place_forget()
                    self.select_button.place_forget()
                    self.scale_txt.place_forget()
        except Exception as e:
            image_path = None
            self.path_txt.config(text="???")

            self.hint("错误，图像选择失败", "#FF0000")
            self.scale.place_forget()
            self.select_button.place_forget()
            self.scale_txt.place_forget()

            print(e)

    def start(self):
        global pixel
        print("设定像素:" + str(pixel))
        ba = BackEnd(self)

class BackEnd():
    def __init__(self, fe):
        global image_path   # 实例化变量
        global pixel
        global mis
        global img_name
        global user_name

        self.path = image_path         # 文件路径
        self.pixel = pixel      # 目标像素值
        self.mis = mis      # 误差阈值
        self.img_weight = img_weight        # 图片边长
        self.img_name = img_name    # 图像名
        self.color = []     # 有几种不像的颜色
        self.result = []    # 计算后的颜色
        self.length = self.img_weight // self.pixel     # 每行长度
        self.user_name = user_name      # 用户名
        self.fe = fe

        self.fe.hint("转换中", "#949412")
        self.average_color()
        print("转化开始")

    def debug(self, file, name = "loss"):       # 测试时使用，用于保存文件（列表）     传入参数：要保存的列表, 文件名(不加后缀)
        with open(f"{self.user_name}" + f"\\Downloads\\{str(name)}.json", "w", encoding="utf-8") as f:
            temp = json.dumps(file, indent=1, ensure_ascii=False) + f"\n\n\n列表元素个数{len(file)}"
            f.write(temp)
            print("(Debug)保存成功")

    def average_color(self):
        try:
            img = Image.open(self.path)
            k_in = 0
            m_in = 0        # 监测k和m循环了几次，仅在调试时有用，可删除

            for i in range(0, self.length ** 2):
                for k in range(0, self.pixel):
                    k_in += 1
                    for m in range(0, self.pixel):
                        m_in += 1
                        local_pixel = list(img.getpixel(((i %  self.length) * self.pixel + m, (i // self.length) * self.pixel + k)))

                        if len(local_pixel) == 3:   # 如果是RGB通道就增加A通道
                            local_pixel.append(255)

                        if k == 0 and m == 0:    # 判断是不是第一个像素
                            self.color.append([])
                            self.color[0].append(local_pixel)
                        else:
                            m_index = 0
                            for y in self.color:
                                if abs(y[0][0] - local_pixel[0]) <= self.mis and abs(y[0][1] - local_pixel[1]) <= self.mis and abs(y[0][2] - local_pixel[2]) <= self.mis:     # 判断是否在阈值内
                                    self.color[m_index].append(local_pixel)
                                    break
                                else:
                                    m_index += 1
                                    self.color.append([])
                                self.color[len(self.color) - 1].append(local_pixel)

                max_num = 0     # 监测哪个颜色块最多
                index = 0
                for p in self.color:
                    if len(p) > len(self.color[max_num]):
                        max_num = index
                    index += 1
                # print(max_num)
                # print(self.color)
                avg = [round(sum(channel) / len(channel)) for channel in zip(self.color[max_num][0])]   
                self.result.append(avg)

                self.color = []

            self.save()
            # print(str(k_in) + ": " + str(m_in))
            # print(self.result)
            # self.debug(self.result, "result")
        except Exception as e:
            self.fe.hint(f"转化失败, 错误:\n{e}", "#FF0000")

    def save(self):     # 保存图片
        num = -1
        img = Image.new("RGBA", (self.img_weight, self.img_weight))
        for i in self.result:
            num += 1
            for k in range(0, self.pixel):
                for m in range(0, self.pixel):
                    position = num // self.length * self.pixel + k, num % self.length * self.pixel + m
                    color = self.result[num]        # 设定当前像素的颜色
                    img.putpixel((position[0], position[1]), (color[0], color[1], color[2], color[3]))
            
        img = img.rotate(-90)
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

        save_dir = f"{self.user_name}\\Downloads"
        for i in range(0, 10):
            ran = random.randint(1000000, 9999999)
            try:
                save_path = os.path.join(save_dir, f"{self.img_name} {str(ran)}.png")
                img.save(save_path)
                self.fe.hint(f"文件已保存至{save_dir}\\{self.img_name} {str(ran)}.png", "#0DB832")
                break
            except Exception as e:
                if i == 9:
                     print(f"保存失败   {e}")
                     self.fe.hint(f"保存失败，错误:\n{e}", "#FF0000")
                pass

if __name__ == "__main__":    
    fe = FrontEnd()
