import tkinter as tk
from tkinter import messagebox
import random as rd

FPS = 300 # 刷新间隔300ms

CELL_SIZE = 30
COLUMN_NUM = 12
ROW_NUM = 25
height = CELL_SIZE * ROW_NUM
width = CELL_SIZE * COLUMN_NUM

SHAPES = {
    "O": [(-1, -1), (0, -1), (-1, 0), (0, 0)],
    "Z": [(-1, -1), (0, -1), (0, 0), (1, 0)],
    "S": [(-1, 0), (0, 0), (0, -1), (1, -1)],
    "T": [(-1, 0), (0, 0), (0, -1), (1, 0)],
    "I": [(0, 1), (0, 0), (0, -1), (0, -2)],
    "L": [(-1, 0), (0, 0), (-1, -1), (-1, -2)],
    "J": [(-1, 0), (0, 0), (0, -1), (0, -2)]
}

SHAPESCOLOR = {
    "O": "blue",
    "Z": "Cyan",
    "S": "red",
    "T": "yellow",
    "I": "green",
    "L": "purple",
    "J": "orange",
}

def draw_cell(canvas, column, row, color="#CCCCCC"):
    x0 = column * CELL_SIZE
    y0 = row * CELL_SIZE
    x1 = x0 + CELL_SIZE
    y1 = y0 + CELL_SIZE
    canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2)

def draw_board(canvas, block_list):
    for row in range(ROW_NUM):
        for column in range(COLUMN_NUM):
            cell_type = block_list[row][column]
            if cell_type:
                draw_cell(canvas, column, row, SHAPESCOLOR[cell_type])
            else:
                draw_cell(canvas, column, row)

def draw_cells(canvas, column, row, cell_list, color="#CCCCCC"):
    for cell in cell_list:
        cell_column, cell_row = cell
        column_i = cell_column + column
        row_i = cell_row + row
        if 0 <= column < COLUMN_NUM and 0 <= row < ROW_NUM:
            draw_cell(canvas, column_i, row_i, color)

win = tk.Tk()
canvas = tk.Canvas(win, width=width, height=height) # 创建窗口
canvas.pack()

#draw_blank_board(canvas) # 初始化背板

block_list = []
for i in range(ROW_NUM):
    i_row = ['' for j in range(COLUMN_NUM)]
    block_list.append(i_row)

draw_board(canvas, block_list) # 新的初始化方式

# draw_cells(canvas, 3, 3, SHAPES["O"], SHAPESCOLOR["O"])

def draw_block_move(canvas, block, direction=[0, 0]): # 方块移动操作，不传direction参数默认不动
    shape_type = block['kind']
    col, row = block['cr']
    cell_list = block['cell_list']

    draw_cells(canvas, col, row, cell_list) # 用灰色把原来的“擦掉”

    delta_c, delta_r = direction
    new_col = col + delta_c
    new_row = row + delta_r
    block['cr'] = [new_col, new_row]

    draw_cells(canvas, new_col, new_row, cell_list, SHAPESCOLOR[shape_type]) # 在新的位置填上

def generate_new_block():
    kind = rd.choice(list(SHAPES.keys()))
    cr = [COLUMN_NUM//2, 0]
    new_block = {
        "kind": kind,
        "cr": cr,
        "cell_list": SHAPES[kind]
    }

    return new_block

def check_move(block, direction=[0, 0]):
    col, row = block['cr']
    cell_list = block['cell_list']

    for cell in cell_list:
        cell_column, cell_row = cell
        c = cell_column + col + direction[0]
        r = cell_row + row + direction[1]
        if c < 0 or c >= COLUMN_NUM or r >= ROW_NUM:
            return False
        if r>=0 and block_list[r][c]:
            return False

    return True

def save_block_to_list(block):
    shape_type = block['kind']
    col, row = block['cr']
    cell_list = block['cell_list']

    for cell in cell_list:
        cell_column, cell_row = cell
        c = cell_column + col
        r = cell_row + row
        block_list[r][c] = shape_type

def lr_move_block(event): # 左右键操控方块
    direction = [0, 0]
    if event.keysym == "Left":
        direction = [-1, 0]
    elif event.keysym == "Right":
        direction = [1, 0]
    else:
        return

    global current_block
    if current_block is not None and check_move(current_block, direction):
        draw_block_move(canvas, current_block, direction)

def rotate_block(event): # 上键右旋90度方块
    global current_block
    if current_block is None:
        return

    cell_list = current_block['cell_list']
    rotate_list = []
    for cell in cell_list:
        cell_column, cell_row = cell
        rotate_cell = [cell_row, -cell_column] # 右旋
        rotate_list.append(rotate_cell)

    block_after_rotate = {
        'kind': current_block['kind'],
        'cell_list': rotate_list,
        'cr': current_block['cr']
    }

    if check_move(block_after_rotate):
        col, row = current_block['cr']
        draw_cells(canvas, col, row, current_block['cell_list']) # 清除原来的
        draw_cells(canvas, col, row, rotate_list, SHAPESCOLOR[current_block['kind']]) # 画旋转后新的
        current_block = block_after_rotate

def land(event): # 下键直接落地
    global current_block
    if current_block is None:
        return

    cell_list = current_block['cell_list']
    col, row = current_block['cr']
    min_height = ROW_NUM # 下降高度
    for cell in cell_list:
        cell_column, cell_row = cell
        c = cell_column + col
        r = cell_row + row
        if block_list[r][c]:
            return
        h = 0
        for row_i in range(r+1, ROW_NUM):
            if block_list[row_i][c]:
                break
            else:
                h += 1
        if h < min_height:
            min_height = h

    down = [0 , min_height]
    if check_move(current_block, down):
        draw_block_move(canvas, current_block, down)

def game_loop():
    win.update()

    global current_block
    if current_block is None:
        new_block = generate_new_block()
        draw_block_move(canvas, new_block)
        current_block = new_block
        if not check_move(current_block):
            messagebox.showinfo("Game Over", "Your Score: %s" % score)
            win.destroy()
            return
    else:
        if check_move(current_block, [0, 1]):
            draw_block_move(canvas, current_block, [0, 1])
        else:
            save_block_to_list(current_block)
            current_block = None

    check_and_clear()

    win.after(FPS, game_loop)

score = 0
win.title("Score: "+str(score))


def check_row_complete(row):
    for cell in row:
        if cell == '':
            return False

    return True

def check_and_clear():
    has_complete_row = False
    for row_i in range(len(block_list)):
        if check_row_complete(block_list[row_i]):
            has_complete_row = True

            if row_i > 0: # 如果不是最上面那一行，所有行下移一格
                for current_row_i in range(row_i, 0 , -1):
                    block_list[current_row_i] =  block_list[current_row_i-1][:]
                block_list[0] = ['' for j in range(COLUMN_NUM)]
            else:
                block_list[row_i] = ['' for j in range(COLUMN_NUM)]

            global score
            score += 10

    if has_complete_row:
        draw_board(canvas, block_list)
        win.title("Score: %s" % score)



canvas.focus_set()
canvas.bind("<KeyPress-Left>", lr_move_block)
canvas.bind("<KeyPress-Right>", lr_move_block)
canvas.bind("<KeyPress-Up>", rotate_block)
canvas.bind("<KeyPress-Down>", land)

current_block = None

win.update()
win.after(FPS, game_loop)

win.mainloop()