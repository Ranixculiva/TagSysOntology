from cmath import rect
from tkinter import *
import threading
from owlready2 import *
from TagSys import TagSys_onto


class Menu:
    def __init__(self, canvas, px=0, py=0, options=[], callbacks=[]) -> None:
        self.tag = f'Menu{id(self)}'
        self._options = options
        self.canvas = canvas
        self.texts = []
        self.rectangles = []
        self.anchor = (0, 0)  # top left corner
        self._pos = (px, py)
        self._h = 0
        self._w = 50
        self.textBox_h = 20
        self.callbacks = callbacks
        self.isMenuShown = False

    def show(self):
        self.isMenuShown = True
        self.update()

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, p):
        self._pos = (p[0], p[1])
        self.moveTo(p[0], p[1])

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, op):
        if isinstance(op, list):
            self._options = list(map(str, op))
            if self.isMenuShown:
                self.update()
        else:
            print('options is not a list')
    # option based on 1

    def highlightOption(self, index):
        for r in self.rectangles:
            self.canvas.itemconfig(r, fill='white')
        if index == False:
            return
        self.canvas.itemconfig(self.rectangles[index-1], fill='SkyBlue')

    # return False if (px,py) is not in menu
    # else return index based on 1

    def isIn(self, px, py):
        x = self.position[0] - self.anchor[0]*self._w
        y = self.position[1] - self.anchor[1]*self._h
        if x <= px and\
                y <= py and\
                x+self._w >= px and\
                y+self._h >= py:
            return max(min(int((py-y)/(self.textBox_h))+1, len(self.rectangles)), 1)
        return False

    def moveTo(self, px, py):
        self._pos = (px, py)
        if self.isMenuShown:
            x = self.position[0] - self.anchor[0]*self._w
            y = self.position[1] - self.anchor[1]*self._h
            for i, r in enumerate(self.rectangles):
                self.canvas.coords(r, x, y+(i)*self.textBox_h,
                                   x+self._w, y+(i+1)*self.textBox_h)
            for i, t in enumerate(self.texts):
                self.canvas.coords(t, x+self._w/2, y+self.textBox_h*(.5+i))

    def update(self):
        self.rectangles = []
        self.texts = []
        self._h = self.textBox_h*len(self.options)

        # top left corner
        x = self.position[0] - self.anchor[0]*self._w
        y = self.position[1] - self.anchor[1]*self._h

        for i, op in enumerate(self.options):
            rectangle = self.canvas.create_rectangle(
                x, y+(i)*self.textBox_h, x+self._w, y+(i+1)*self.textBox_h, fill='white', tag=(self.tag,))
            t = self.canvas.create_text(
                x+self._w/2, y+self.textBox_h*(.5+i), text=op, font='TkMenuFont', fill='black', tag=(self.tag,))

            self.rectangles.append(rectangle)
            self.texts.append(t)
            self.canvas.tag_bind(self.tag, '<Enter>', self.object_enter_event)
            self.canvas.tag_bind(self.tag, '<Leave>', self.object_leave_event)
            self.canvas.tag_bind(self.tag, '<ButtonRelease-1>',
                                 self.mouse_left_release)

    def object_enter_event(self, e):
        self.highlightOption(self.isIn(e.x, e.y))

    def object_leave_event(self, e):
        self.highlightOption(False)

    def mouse_left_release(self, e):
        self.canvas.delete(self.tag)
        c = self.isIn(e.x, e.y)
        callbacks = self.callbacks
        del self
        for f in callbacks:
            th = threading.Thread(target=f, args=(c,))
            th.setDaemon(True)
            th.start()


class RectangleGenBlock:
    cur_selected = None
    def __init__(self, canvas, gfg, color='black', text='NoText', textColor='red',x0=0,y0=0,w=50,h=50, isLine = False):
        self.gfg = gfg
        self.isLine = isLine
        #Tag_sys
        self.genBlock = None


        self.isIn=False
        self.canvas = canvas
        self.tag = f'Component{id(self)}'
        self.w = w
        self.h = h
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1 = x0+self.w
        self.y1 = y1 = y0+self.h
        if isLine:
            self.rectangle = canvas.create_line(
                self.x0, self.y0, self.x1, self.y1, fill=color, dash=True, tag=(self.tag))
        else:
            self.rectangle = canvas.create_rectangle(
                self.x0, self.y0, self.x1, self.y1, fill=color, tag=(self.tag))
        self.text = canvas.create_text((x0+x1)/2, (y0+y1)/2, text=text,
                                       font='TkMenuFont', fill=textColor, tag=(self.tag))
        self.popMenu = False
        self.lineLinks = {}

        self.attached_blocks = set()

        self.canvas.tag_bind(self.tag, '<Enter>', self.object_enter_event)
        self.canvas.tag_bind(self.tag, '<Leave>', self.object_leave_event)
        self.canvas.tag_bind(self.tag, '<Button-1>', self.mouse_left_click)
        self.canvas.tag_bind(self.tag, '<ButtonRelease-1>',
                             self.mouse_left_release)
        self.canvas.tag_bind(self.tag, "<B1-Motion>", self.move_object)

        self.isMenuShown = False
        self.menu = None

        self.X_relative_to_cur_rect = 0
        self.Y_relative_to_cur_rect = 0
    def delete(self):
        self.canvas.delete(self.tag)
        for l in self.lineLinks:
            l.delete()



    def move_object(self, e):
        x = self.X_relative_to_cur_rect
        y = self.Y_relative_to_cur_rect

        self.moveTo(e.x-x, e.y-y)
        if self.menu:
            self.menu.position = (self.x1, self.y0)

    def object_enter_event(self, e):
        self.isIn = True
        if not self.isLine:
            self.canvas.itemconfig(self.rectangle, outline='SkyBlue')
        else:
            self.canvas.itemconfig(self.rectangle, fill='SkyBlue')


    def object_leave_event(self, e):
        self.isIn = False
        color = 'black'
        width = 1
        if RectangleGenBlock.cur_selected == self:
            color = 'yellow'
            width = 3
        if not self.isLine:
            self.canvas.itemconfig(self.rectangle, outline=color,width=width)
        else:
            self.canvas.itemconfig(self.rectangle, fill=color,w=width)

    def mouse_left_click(self, e):
        r = self
        if not self.isLine:
            self.canvas.itemconfig(self.rectangle, outline='Blue')
        else:
            self.canvas.itemconfig(self.rectangle, fill='Blue')
        self.X_relative_to_cur_rect = e.x - (r.x0 + r.w/2)
        self.Y_relative_to_cur_rect = e.y - (r.y0 + r.h/2)
        if RectangleGenBlock.cur_selected:
            if not RectangleGenBlock.cur_selected.isLine:
                self.canvas.itemconfig(RectangleGenBlock.cur_selected.rectangle, outline='Blue',width=1)
            else:
                self.canvas.itemconfig(RectangleGenBlock.cur_selected.rectangle, fill='Blue',w=1)
        if RectangleGenBlock.cur_selected != self:
            RectangleGenBlock.cur_selected = self
            self.gfg.update_tag_frame()
            


    def mouse_left_release(self, e):
        if not self.isLine:
            self.canvas.itemconfig(self.rectangle, outline='SkyBlue')
        else:
            self.canvas.itemconfig(self.rectangle, fill='SkyBlue')
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        r = self
        r.moveTo(min(max(r.w/2, r.x0+r.w/2), w-r.w/2),
                 min(max(r.h/2, r.y0+r.h/2), h-r.h/2))

        def g(c):
            self.isMenuShown = False
        if self.popMenu:
            if not self.isMenuShown:
                self.isMenuShown = True
                #TODO:MENU
                
                #self.menu = Menu(self.canvas, self.x1, self.y0, [
                #    124, 124, 21234245], [lambda c:print(c), g])
                #self.menu.show()
                
    def moveTo(self, px, py, offsetX=0, offsetY=0):
        for b in self.attached_blocks:
            if not b.isLine: 
                b.moveTo(px, py,offsetX+(b.x0-self.x0)+(b.w/2-self.w/2),offsetY+(b.y0-self.y0)+(b.h/2-self.h/2))        
    
        self.x0 = px-self.w/2+offsetX
        self.y0 = py-self.h/2+offsetY
        self.x1 = px+self.w/2+offsetX
        self.y1 = py+self.h/2+offsetY

        self.canvas.coords(self.rectangle,
                           self.x0,
                           self.y0,
                           self.x1,
                           self.y1)

        self.canvas.coords(self.text, (self.x0+self.x1)/2, (self.y0+self.y1)/2)
        for l in self.lineLinks.keys():
            l.update()
        for b in self.attached_blocks:
            if b.isLine: 
                b.update()

    #def isIn(self, px, py):
    #    return self.x0 <= px and\
    #        self.y0 <= py and\
    #        self.x1 >= px and\
    #        self.y1 >= py
class RectangleBlock(RectangleGenBlock):
    def __init__(self, canvas, gfg, color='black', text='NoText', textColor='red',x0=0,y0=0,w=50,h=50):
        
        
        
        super().__init__(canvas, gfg, color=color, text=text, textColor=textColor,x0=x0,y0=y0,w=w,h=h)
        
        ## TagSys
        self.genBlock = TagSys_onto.Block()
        self.genBlock.update_candidates()
        self.rec_port_blocks = []
        
    def delete(self):
        destroy_entity(self.genBlock)
        print(TagSys_onto.Block.instances())
        super().delete()
    def __iadd__(self, rec_port_block):
        self.genBlock+=rec_port_block.genBlock
        self.attached_blocks.add(rec_port_block)
        rec_port_block.genBlock.update_candidates()
        return self
    def generate_rec_portBlock(self, isLeft=False):

        w=14
        h=14
        y0=self.y0/2+self.y1/2-h/2
        offsetX = 0
        if isLeft:
            offsetX = -self.w-w
        x0=self.x1+offsetX

        rec_port_block = RectanglePortBlock(self.canvas, self.gfg,color='gray',text='p',textColor = 'blue',x0= x0,y0 = y0 ,w=w ,h=h )
        self.rec_port_blocks.append(rec_port_block)
        self+=rec_port_block
        return rec_port_block

class RectanglePortBlock(RectangleGenBlock):
    def __init__(self, canvas, gfg, color='black', text='NoText', textColor='red',x0=0,y0=0,w=50,h=50):
        
        super().__init__(canvas, gfg, color=color, text=text, textColor=textColor,x0=x0,y0=y0,w=w,h=h)
        ## TagSys
        self.genBlock = TagSys_onto.PortBlock()
        self.rec_slot_blocks = []
    def delete(self):
        destroy_entity(self.genBlock)
        print(TagSys_onto.PortBlock.instances())
        super().delete()
    def __iadd__(self,rec_slot_block):
        self.genBlock+=rec_slot_block.genBlock
        self.attached_blocks.add(rec_slot_block)
        rec_slot_block.genBlock.update_candidates()
        return self
    def generate_rec_slotBlock(self,isLeft = False):
        w=12
        h=12
        y0=self.y0/2+self.y1/2-h/2
        offsetX = 0
        if isLeft:
            offsetX = -self.w-w-10
        x0=self.x1+5+offsetX
        rec_slot_block = RectangleSlotBlock(self.canvas, self.gfg,color='orange',text='s',textColor = 'black',x0= x0,y0 = y0 ,w=w ,h=h )
        self.rec_slot_blocks.append(rec_slot_block)
        self+=rec_slot_block
        return rec_slot_block

class RectangleSlotBlock(RectangleGenBlock):
    def __init__(self, canvas, gfg, color='black', text='NoText', textColor='red',x0=0,y0=0,w=50,h=50):
        
        super().__init__(canvas, gfg, color=color, text=text, textColor=textColor,x0=x0,y0=y0,w=w,h=h)
        ## TagSys
        self.genBlock = TagSys_onto.SlotBlock()
    def delete(self):
        destroy_entity(self.genBlock)
        print(TagSys_onto.SlotBlock.instances())
        super().delete()

        #return super().moveTo(px, py, offsetX=offsetX, offsetY=offsetY)

class RectangleLinkBlock(RectangleGenBlock):
    def __init__(self, canvas, gfg, color='black', text='NoText', textColor='red',x0=0,y0=0,w=50,h=50):
        
        super().__init__(canvas, gfg, color=color, text=text, textColor=textColor,x0=x0,y0=y0,w=w,h=h,isLine = True)
        ## TagSys
        self.genBlock = TagSys_onto.LinkBlock()
        self.rec_slot_blocks = []

        self.rect1 = None
        self.rect2 = None
    def delete(self):
        destroy_entity(self.genBlock)
        print(TagSys_onto.SlotBlock.instances())
        super().delete()
    def update(self):
        r1, r2 = self.rect1,self.rect2
        if r1.x0 > r2.x0:
            r1,r2 = r2,r1
        self.x1=r2.x0-1
        self.y1=(r2.y0+r2.y1)/2
        self.y0=(r1.y0+r1.y1)/2
        self.x0=r1.x1+1
        self.canvas.coords(self.rectangle, self.x0,self.y0,self.x1,self.y1)
        self.canvas.coords(self.text, (self.x0+self.x1)/2,(self.y0+self.y1)/2,)
        
    def __iadd__(self,rec_slot_block):
        self.genBlock+=rec_slot_block.genBlock
        self.attached_blocks.add(rec_slot_block)
        self.genBlock.update_candidates()
        return self
    def moveTo(self, px, py, offsetX=0, offsetY=0):
        pass
    def generate_rec_slotBlock(self,isLeft = False):
        w=12
        h=12
        y0=self.y0/2+self.y1/2-h/2
        offsetX = 0
        if isLeft:
            offsetX = -self.w-w-10
        x0=self.x1+5+offsetX
        rec_slot_block = RectangleSlotBlock(self.canvas, self.gfg,color='orange',text='s',textColor = 'black',x0= x0,y0 = y0 ,w=w ,h=h )
        self.rec_slot_blocks.append(rec_slot_block)
        self+=rec_slot_block
        return rec_slot_block

#deprecated
class LineLink:
    def __init__(self, canvas, rect1, rect2, color='black'):
        self.canvas = canvas
        self.rect1 = rect1
        self.rect2 = rect2
        self.tag = f'LineLink{id(self)}'
        self.line = canvas.create_line(
            0, 0, 0, 0, fill=color, dash=True, tag=(self.tag,))
        rect1.lineLinks[self] = len(rect1.lineLinks)
        rect2.lineLinks[self] = len(rect2.lineLinks)
        self.update()
    def delete(self):
        self.canvas.delete(self.tag)
    def update(self):
        rect1 = self.rect1
        rect2 = self.rect2

        if rect1.x1 < rect2.x1:
            rect1, rect2 = rect2, rect1

        rect1_n = len(rect1.lineLinks)
        rect1_i = rect1.lineLinks[self]

        rect2_n = len(rect2.lineLinks)
        rect2_i = rect2.lineLinks[self]

        x0 = rect2.x1
        y0 = (rect2.y1-rect2.y0)*(rect2_i+1)/(rect2_n+1) + rect2.y0
        x1 = rect1.x0
        y1 = (rect1.y1-rect1.y0)*(rect1_i+1)/(rect1_n+1) + rect1.y0
        self.canvas.coords(self.line, x0, y0, x1, y1)


class GFG:
    def __init__(self, master=None):
        self.rectangleBlocks = set()
        self.currentRectangle = None
        self.line_links = set()
        self.currentLineLink = None
        self.selection = []
        self.master = master
        self.allTags = sorted(TagSys_onto.Tag.descendants(),key=lambda e:e.name)

        # canvas object to create shape
        # creating button
        main_frame = PanedWindow(relief='groove', borderwidth=10,
                                 bg='blue', width=700, height=400)
        tool_frame = Frame(relief='groove', borderwidth=5,
                           bg='red', width=80, height=300)
        tag_frame=self.tag_frame = Frame(relief='groove', borderwidth=5,
                           bg='red', width=200, height=300)
        self.canvas = Canvas(bg='green')

        tool_frame.pack(side='left', fill='both')
        self.canvas.pack(side='left', fill='both')
        main_frame.pack(side='left', fill='both', expand=True)

        tag_frame.pack(side='left', fill='both')
        self.canvas.pack(side='left', fill='both')
        main_frame.pack(side='left', fill='both', expand=True)

        main_frame.add(tool_frame)
        main_frame.add(tag_frame)
        main_frame.add(self.canvas)

        def block_button_command(): return self.generate_block(
            color='red', text='Block', textColor='black')
        block_button = Button(tool_frame, text='Block', width=10,
                      height=1, bd='1', command=block_button_command)
        block_button.pack(fill='x')

        connect_button = Button(tool_frame, text='Connect', width=10,
                      height=1, bd='1', command=self.generate_link)
        connect_button.pack(fill='x')


        
        def print_info():
            if RectangleGenBlock.cur_selected:
                genBlock = RectangleGenBlock.cur_selected.genBlock
                print(f"{genBlock.name}{tuple(genBlock.hasTag)} has candidates: {genBlock.hasCandidate}")
        info_button = Button(tool_frame, text='info', width=10,
                      height=1, bd='1', command=print_info)
        info_button.pack(fill='x')

        def clear_block():
            if RectangleBlock.cur_selected:
                RectangleBlock.cur_selected.delete()
            RectangleBlock.cur_selected = None

        clear_button = Button(tool_frame, text='Delete', width=10,
                      height=1, bd='1', command=clear_block)
        clear_button.pack(fill='x')


        master.bind("<B1-Motion>", lambda e: self.motion(e))
        master.bind('<Button-1>', lambda e: self.mouse_left_click(e))
        master.bind('<ButtonRelease-1>', lambda e: self.mouse_left_release(e))

        self.canvas.bind('<Button-1>', lambda e: self.mouse_left_click_on_canvas(e))

    def show(self, text):
        print(text)

    def generate_block(self, color, text, textColor,w=50,h=50):
        r = RectangleBlock(self.canvas, self, color, text, textColor,w=w,h=h)

        self.rectangleBlocks.add(r)

    def motion(self, e):
        pass
        # if self.currentRectangle:
    def mouse_left_click(self, e):
        pass
    def mouse_left_click_on_canvas(self, e):
        # print(f'{e.x}, {e.y}')
        # for r in list(self.rectangles):
        #     if r.isIn(e.x, e.y):
        #         self.currentRectangle = r
        #         break
        
        selected_rectangle = RectangleGenBlock.cur_selected
        if not RectangleGenBlock.cur_selected:return 
        

        if not selected_rectangle.isIn:#(e.x,e.y):
            RectangleGenBlock.cur_selected = None
            if not selected_rectangle.isLine:
                self.canvas.itemconfig(selected_rectangle.rectangle, outline='black',width=1)
            else:
                self.canvas.itemconfig(selected_rectangle.rectangle, fill='black',w=1)
            self.clear_tag_frame()

    def clear_tag_frame(self):
        for widget in self.tag_frame.winfo_children():
            widget.destroy()
    def update_tag_frame(self):
        self.clear_tag_frame()
        def chkCallBack(_tag):
            if not RectangleGenBlock.cur_selected: return 
            genBlock = RectangleGenBlock.cur_selected.genBlock
            genBlock << _tag
            genBlock.update_candidates()


        i=0
        for tag in self.allTags:
            if not RectangleGenBlock.cur_selected: return 
            genBlock = RectangleGenBlock.cur_selected.genBlock
            button = Checkbutton(self.tag_frame, text=tag.name, command= lambda _tag = tag: chkCallBack(_tag)) 
            if tag in genBlock.hasTag: button.toggle()
            button.grid(sticky = W, column=0,row=i)
            i+=1


    def mouse_left_release(self, e):
        # if r := self.currentRectangle:
        #     self.currentRectangle = None
        pass

    def generate_link(self):
        for r in self.rectangleBlocks:
            r.popMenu = True
        self.show('Link mode')
        self.show('Please select 2 components')
        self.link_select_component_bind_id = self.master.bind(
            '<ButtonRelease-1>', lambda e: self.link_select_component(e))

    def link_select_component(self, e):
        bind_id = self.link_select_component_bind_id
        for r in list(self.rectangleBlocks):
            if r.isIn:#(e.x, e.y):
                self.selection.append(r)
                break
        else:
            self.master.unbind('<ButtonRelease-1>', bind_id)
            self.show('Link canceled')
            for r in self.rectangleBlocks:
                r.popMenu = False
            return

        if len(self.selection) == 2:
            rec_block1, rec_block2 = self.selection
            if rec_block1.x0 > rec_block2.x0:
                rec_block1, rec_block2=rec_block2, rec_block1
            ## main section
            p1 = rec_block1.generate_rec_portBlock()
            p2 = rec_block2.generate_rec_portBlock(isLeft=True)
            s1 = p1.generate_rec_slotBlock()
            s2 = p2.generate_rec_slotBlock(isLeft=True)
            
            

           
            w=s2.x0-s1.x1-1
            h=(s2.y0+s2.y1)/2 - (s1.y0+s1.y1)/2
            y0=(s1.y0+s1.y1)/2
            x0=s1.x1+1
            l1 = RectangleLinkBlock(self.canvas, self,color='black',text='link',textColor = 'blue',x0= x0,y0 = y0 ,w=w ,h=h )
            l1.rec_slot_blocks.append(s1)
            l1.rec_slot_blocks.append(s2)
            s1.attached_blocks.add(l1)
            s2.attached_blocks.add(l1)
            l1.rect1 = s1
            l1.rect2 = s2
            l1+=s1
            l1+=s2
            l1.genBlock.update_candidates()
            
            #self.currentLineLink = LineLink(self.canvas, r1, r2)
            ##
            self.master.unbind('<ButtonRelease-1>', bind_id)
            self.selection = []
            self.show('2 selected')
            self.show('Link successfully created')
            for r in self.rectangleBlocks:
                r.popMenu = False
            return
        self.show('1 selected')


if __name__ == "__main__":

    master = Tk()
    master.title("Sysmaker")
    gfg = GFG(master)
    mainloop()
