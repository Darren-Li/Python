

# 字体路径，需要展现什么字体就把该字体路径+后缀名写上，如：font_path = '黑体.ttf'
font_path : string

# 输出的画布宽度，默认为400像素
width : int (default=400)
# 输出的画布高度，默认为200像素
height : int (default=200)

# 词语水平方向排版出现的频率，默认 0.9 （所以词语垂直方向排版出现频率为 0.1)
prefer_horizontal : float (default=0.90)

# 如果参数为空，则使用二维遮罩绘制词云。如果 mask 非空，设置的宽高值将被忽略，遮罩形状被 mask 取代。
# 除全白（#FFFFFF）的部分将不会绘制，其余部分会用于绘制词云。如：bg_pic = imread('读取一张图片.png')，
# 背景图片的画布一定要设置为白色（#FFFFFF），然后显示的形状为不是白色的其他颜色。可以用ps工具将自己要显示
# 的形状复制到一个纯白色的画布上再保存。
mask : nd-array or None (default=None)

# 按照比例进行放大画布，如设置为1.5，则长和宽都是原来画布的1.5倍。
scale : float (default=1)

# 显示的最小的字体大小
min_font_size : int (default=4)
# 字体步长，如果步长大于1，会加快运算但是可能导致结果出现较大的误差。
font_step : int (default=1)
# 要显示的词的最大个数
max_words : number (default=200)

# 设置需要屏蔽的词，如果为空，则使用内置的STOPWORDS
stopwords : set of strings or None

# 背景颜色，如background_color='white',背景颜色为白色。
background_color : color value (default="black")

 # 显示的最大的字体大小
max_font_size : int or None (default=None)

# 当参数为“RGBA”并且background_color不为空时，背景为透明。
mode : string (default=”RGB”)
# 词频和字体大小的关联性
relative_scaling : float (default=.5)
# 生成新颜色的函数，如果为空，则使用 self.color_func
color_func : callable, default=None
# 使用正则表达式分隔输入的文本
regexp : string or None (optional)
# 是否包括两个词的搭配
collocations : bool, default=True
# 给每个单词随机分配颜色，若指定color_func，则忽略该方法。
colormap : string or matplotlib colormap, default=”viridis”
# 根据词频生成词云
fit_words(frequencies)

# 根据文本生成词云
generate(text)

# 根据词频生成词云
generate_from_frequencies(frequencies[, ...])

# 根据文本生成词云
generate_from_text(text)
# 将长文本分词并去除屏蔽词（此处指英语，中文分词还是需要自己用别的库先行实现，使用上面的 fit_words(frequencies) ）
process_text(text)
# 对现有输出重新着色。重新上色会比重新生成整个词云快很多。
recolor([random_state, color_func, colormap])
# 转化为 numpy array
to_array()
# 输出到文件
to_file(filename)
