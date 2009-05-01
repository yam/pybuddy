import time

################
#Configuration
################
tsleep = 0.1

#########################################
# Decoding macros
##########################################

def macro_color (red,green,blue):
    message = "C:%d:%d:%d" % (red,green,blue)
    message += "\nX\nS\nZ\nZ\n"
    return message

def macro_heart ():
    message = "H:1"
    message += "\nX\nS\nZ\nZ\n"
    return message

def macro_move_flap():
    message  = "ML\nX\nS\nS\n"
    message += "MR\nX\nS\nS\n"
    message += "ML\nX\nS\nS\n"
    return message + macro_flap()

def macro_flap (heart=0):
    message = ""
    for i in range(2):
        message += "L\n"
        message += "WU\n"
        if heart:
            message += "H:1\n"
        message += "X\nS\nL\n"
        message += "WD\nX\nS\n"
    return message

def macro_heart2():
    message = "H:1\nX\nS\n"
    message += "Z\nS\n"
    message += "H:1\nX\nS\n"
    message += "Z\nS\n\nZ\nZ\n"
    return message

def macro_demo(num=1):
    message = ""
    for i in range(num):
        message += "C:1:0:0\nH:0\nML\nWD\nX\nS\nS\n"
        message += "C:0:1:0\nH:1\nMR\nWU\nX\nS\nS\n"
        message += "C:0:0:1\nH:0\nML\nWD\nX\nS\nS\n"
        message += "C:1:0:1\nH:1\nMR\nWU\nX\nS\nS\n"
        message += "C:1:1:0\nH:0\nML\nWD\nX\nS\nS\n"
        message += "C:0:1:1\nH:1\nMR\nWU\nX\nS\nS\n"
        message += "C:1:1:1\nH:0\nML\nWD\nX\nS\nS\n"
        message += "Z\nZ\n"
    return message

def do_color(buddy,red,green,blue):
    r,g,b = buddy.getColors()
    try:
         param1=int(red)
         param2=int(green)
         param3=int(blue)
    except:
         param1=-1
         param2=-1
         param3=-1

    if(param1==-1):
        param1=r

    if(param2==-1):
        param2=g

    if(param3==-1):
        param3=b

    buddy.setHeadColor(param1,param2,param3)



def decode_buddy (buddy,msg):
    orders = msg.split("\n")
    for str in (orders):
        cod = str.split(":")
        param=0
        if cod[0] == 'RED' or cod[0]=='R':
            try: do_color(buddy,cod[1],-1,-1)
            except: pass
        elif cod[0] == 'GREEN' or cod[0]=='G':
            try: do_color(buddy,-1,cod[1],-1)
            except: pass
        elif cod[0] == 'BLUE' or cod[0]=='B':
            try: do_color(buddy,-1,-1,cod[1])
            except: pass
        elif cod[0] == 'YELLOW':
            try: do_color(buddy,cod[1],cod[1],-1)
            except: pass
            continue
        elif cod[0] == 'SAPHIRE':
            try: do_color(buddy,-1,cod[1],cod[1])
            except: pass
        elif cod[0] == 'VIOLET':
            try: do_color(buddy,cod[1],-1,cod[1])
            except: pass
        elif cod[0] == 'HEART' or cod[0]=='H':
            try:
                param=int(cod[1])
            except:
                param=0
            buddy.setHeart(param)
        elif cod[0] == 'C':
            try: do_color(buddy,cod[1],cod[2],cod[3])
            except: pass
        elif cod[0] == 'MR':
            buddy.flick(buddy.RIGHT)
            continue
        elif cod[0] == 'ML':
            buddy.flick(buddy.LEFT)
        elif cod[0] == 'SLEEP' or cod[0]=='S':
            time.sleep(tsleep)
        elif cod[0] == 'WU':
            buddy.wing(buddy.UP)
        elif cod[0]== 'WD':
            buddy.wing(buddy.DOWN)
        elif cod[0]== 'EXEC' or cod[0]=='X':
            buddy.pumpMessage()
        elif cod[0] == 'CLEAR' or cod[0]=='L':
            buddy.resetMessage()
        elif cod[0]== 'RESET' or cod[0]=='Z':
            buddy.resetMessage()
            buddy.pumpMessage()
        elif cod[0] == 'MACRO_FLAP':
            decode_buddy(buddy,macro_move_flap())
        elif cod[0] == 'MACRO_FLAP2':
            decode_buddy(buddy,macro_flap())
        elif cod[0] == 'MACRO_RED':
            decode_buddy(buddy,macro_color(1,0,0))
        elif cod[0] == 'MACRO_GREEN':
            decode_buddy(buddy,macro_color(0,1,0))
        elif cod[0] == 'MACRO_BLUE':
            decode_buddy(buddy,macro_color(0,0,1))
        elif cod[0] == 'MACRO_YELLOW':
            decode_buddy(buddy,macro_color(1,1,0))
        elif cod[0] == 'MACRO_VIOLET':
            decode_buddy(buddy,macro_color(1,0,1))
        elif cod[0] == 'MACRO_SAPHIRE':
            decode_buddy(buddy,macro_color(0,1,1))
        elif cod[0] == 'MACRO_LBLUE':
            decode_buddy(buddy,macro_color(1,1,1))
        elif cod[0] == 'MACRO_HEART':
            decode_buddy(buddy,macro_heart())
        elif cod[0] == 'MACRO_HEART2':
            decode_buddy(buddy,macro_heart2())
        elif cod[0] == 'DEMO':
            decode_buddy(buddy,macro_demo())
