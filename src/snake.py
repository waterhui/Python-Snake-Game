#coding=utf-8

import curses
import threading
import random
#import msvcrt
#from curses import textpad
#!!!addch(y,x,ch)

stdscr = curses.initscr() #初始化curses,返回屏幕对象

curses.noecho() #如果在终端上打字,在终端输入一个a就会显示一个a,如果不要这样的效果,就设置noecho
curses.cbreak() #为了按下按键就直接响应为不必再按下enter,就输入模式设置成cbreak,而不是缓冲模式
stdscr.keypad(True) #我们输入过程中有很多特别的键位,比如上下左右,如果我们需要特殊处理这些键位,则可以调用keypad(True),这样当我们按下键盘左键,将会返回一个类似KEY_LEFT的特殊值

gameX = 1 #坐标原点y
gameY = 1 #坐标原点x
gameHeight = 20 #游戏高度
gameWidth = 20 #游戏宽度
gameSpeed = 0.08 #游戏速度
blockSize = 2 #游戏单元像素格
isGameOver = False #判断是否游戏结束,True(结束)

gameScore = 0 #游戏得分
scorePos = [gameHeight // 2, int(gameWidth * 1.5)]  #得分位置

KEY_QUIT = ord('a') #离开键
mutex_Key = True  #按键互斥锁,当有多个按键按下时,只处理当前的按键,其余舍弃



'''
蛇类
'''
class Snake(object):

    def __init__(self, direction):
#蛇身
        self.body = [[gameWidth // 2, y] for y in range (
            gameWidth // 2 - 2, gameWidth // 2 + 3)]
#蛇头方向
        self.direction = direction

'''
食物类
'''
class Food(object):

    def __init__(self):
        self.pos = [gameX,gameY]

    def get_Food(self, snake):
        while True:
            flag = 1
            x = random.randint(gameX, gameWidth - 1 * blockSize)
            y = random.randint(gameY, gameWidth - 1 * blockSize)
            for i in snake.body:
                if x  == i[0] and y == i[1]:
                    flag = 0
                    break
            if flag:
                break
        self.pos = [x,y]



'''
上、下、左、右函数
'''
up    = lambda x:[x[0] - 1, x[1]]
down  = lambda x:[x[0] + 1, x[1]]
left  = lambda x:[x[0], x[1] - 1]
right = lambda x:[x[0], x[1] + 1]

'''
字典move,用于实现switch case
'''
move  = {curses.KEY_UP: up,
         curses.KEY_LEFT: left,
         curses.KEY_DOWN: down,
         curses.KEY_RIGHT: right,
         ord('k'): up,
         ord('h'): left,
         ord('j'): down,
         ord('l'): right
        }

'''
相反方向.传入一个方向,返回其相反的方向
'''
opposite = {curses.KEY_UP: curses.KEY_DOWN,
        curses.KEY_DOWN: curses.KEY_UP,
        curses.KEY_LEFT: curses.KEY_RIGHT,
        curses.KEY_RIGHT: curses.KEY_LEFT,
        ord('k'): ord('j'),
        ord('j'): ord('k'),
        ord('h'): ord('l'),
        ord('l'): ord('h')
        }

'''
游戏边框
'''
def Init_Frame():

    for i in range(0, gameHeight + 1):
        stdscr.addch(0, i * blockSize, '#')
        stdscr.addch(i, 0, '#')
        stdscr.addch(i , gameWidth  * blockSize, '#')
        stdscr.addch(gameHeight , i * blockSize,'#')

'''
初始化蛇身
'''
def Init_Snake(self):
    Draw_Snake(self.body[0], '@')
    for i in self.body[1:]:
        Draw_Snake(i, '*')



'''
画蛇结点(!一个结点)
'''
Draw_Snake = lambda point,ch: stdscr.addch(point[0], point[1] * blockSize, ch)

'''
显示得分
'''
Disp_Score = lambda point,str: stdscr.addstr(point[0], point[1] * blockSize, str, curses.A_REVERSE)

'''
移动后的新蛇结点
'''
def New_Snake(self):
    for i in range(-len(self.body) + 1, 0)[::-1]:
        self.body[i] = self.body[i - 1]

'''
判断蛇头是否接触到食物
'''
def IsTouch(snakePos, foodPos):
    if snakePos == foodPos:
        return True
    return False


'''
判断是否到游戏结束的状态
'''
def IsOver(snake, newPos):
    if newPos[0] < gameX or newPos[1] < gameY:
        return True
    elif newPos[0] > gameWidth - gameX or newPos[1] > gameHeight - gameY:
        return True
    for i in snake.body[3:]:
        if i == newPos:
            return True
    return False

'''
自动移动
'''
def Auto_Move(snake, f):
#使用闭包保存蛇对象snake,食物对象food
    def _Auto_Move():
        nonlocal snake
        nonlocal f
        global gameScore #引用全局变量
        global isGameOver #引用全局变量
        global mutex_Key #引用全局变量
        if not snake.direction == KEY_QUIT:
            if IsOver(snake, move[snake.direction](snake.body[0])):
                isGameOver = True
                return
            if IsTouch(move[snake.direction](snake.body[0]), f.pos):
#如果蛇头接触到食物
                snake.body.insert(0,f.pos)
                f.get_Food(snake)
                Draw_Snake(f.pos, '%')
                gameScore += 1
                Disp_Score(scorePos, str(gameScore))
            else:
                Draw_Snake(snake.body[-1], ' ') #消除旧蛇尾
                New_Snake(snake) #得到新的蛇结点(除了头结点)
                snake.body[0]  = move[snake.direction](snake.body[0]) #得到新的头结点

            Draw_Snake(snake.body[1], '*') #将前头结点用蛇身标志覆盖'*'
            Draw_Snake(snake.body[0], '@') #画出新头结点
            stdscr.refresh()
            mutex_Key = True
            timer = threading.Timer(gameSpeed, _Auto_Move)
            timer.start()
    return _Auto_Move

'''
退出时恢复控制台原有设置
'''
def EndWin():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

'''
main入口
'''
def main():
    Init_Frame()
    s = Snake(curses.KEY_UP)
    Init_Snake(s)
    f = Food()
    f.get_Food(s)
    Draw_Snake(f.pos,'%')
    stdscr.addstr(gameHeight // 2 - blockSize, int(gameWidth * 1.5) * blockSize - blockSize, "score")
    Disp_Score(scorePos, str(gameScore))
    f = Auto_Move(s, f)
    f()
    global mutex_Key #引用全局变量
    while True:
        #if msvcrt.kbhit():  #判断是否有按键按下
        stdscr.nodelay(1) #设置nodelay,为1时,使得控制台可以以非阻塞的方式接受控制台的输入,超时1秒 没什么用
        if isGameOver:
            EndWin()
            return
        ch = stdscr.getch() #返回ASCII码(int)
        if ch == KEY_QUIT:#curses.KEY_F1:
            s.direction = KEY_QUIT
            EndWin()
            return
        if s.direction == ch:
            continue

        try:
            opposite[ch]
        except KeyError:
            continue
        else:
            if s.direction == opposite[ch]:
                continue

        try:
            move[ch]
        except KeyError:
            continue
        else:
            if mutex_Key:
                s.direction = ch
                mutex_Key = False


if __name__ == '__main__':
    main()
