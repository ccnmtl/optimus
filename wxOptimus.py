#!/usr/bin/env python
from wxPython.wx import *
from TileEngine import *
from xml.dom.minidom import parseString
from xml.sax import saxutils
import os,re

BASE_DIR = "simulations"

        

class Log:
    def __init__(self):
        self.messages = []
        self.errors = true
        self.warnings = false
        self.debugs = true 

    def error(self,message):
        self.messages.append(("error",message))

    def warning(self,message):
        self.messages.append(("warning",message))

    def debug(self,message):
        self.messages.append(("debug",message))

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

class Simulation:
    def __init__(self,dir="",name="",description="",federates=[]):
        self.dir = dir
        self.name = name
        self.description = description
        self.federates = federates
        self.optimus = get_optimus()

    def load_from_file(self,dir=""):
        if dir != "":
            self.dir = dir
        xml = open(BASE_DIR + os.sep + self.dir + os.sep +
                "simulation.xml","r").read()
        doc = parseString(xml)
        root = doc.getElementsByTagName("simulation")[0]
        self.name = root.getAttribute('name')
        self.federates = []
        try:
            self.description = getText(doc.getElementsByTagName("description")[0].childNodes)
        except:
            pass # there was no description tag

        try:
            for fed in root.getElementsByTagName("federate"):
                file = fed.getAttribute('file')
                system = fed.getAttribute('system')
                federate = Federate(simulation=self, dir=system, system=system,
                        name=system)
                #federate.load_from_file()
                self.federates.append(federate)
        except:
            pass # no <federates>


    def save(self):
        if self.name == "":
            return
        if self.dir == "":
            self.dir = re.sub(r"\W","_",self.name)

        try:
            os.makedirs(BASE_DIR + os.sep + self.dir)
        except:
            # probably already existed
            pass

        f = open(BASE_DIR + os.sep + self.dir + os.sep + "simulation.xml","w")
        f.write(self.as_xml())
        f.close()

    def as_xml(self):
        return """<?xml version="1.0"?><simulation name=%s>
        <description>%s</description></simulation>""" % \
        (saxutils.quoteattr(self.name), saxutils.escape(self.description))

class Federate:
    def __init__(self, simulation="", dir="", system="", name="", description="", 
            parameters=[], variables=[], handlers=[]):
        self.simulation = simulation
        self.dir = dir
        self.system = system
        self.name = name
        self.description = description
        self.parameters = parameters
        self.variables = variables
        self.handlers = handlers
        self.optimus = get_optimus()

    def load_from_file(self,dir=""):
        if dir != "":
            self.dir = dir
        xml = open(BASE_DIR + os.sep + self.simulation.dir + os.sep +
                self.dir + os.sep + "federate.xml","r").read()
        doc = parseString(xml)
        root = doc.getElementsByTagName("federate")[0]
        self.name = root.getAttribute("name")
        self.system = root.getAttribute("system")
        try:
            self.description = getText(doc.getElementsByTagName("description")[0].childNodes)
        except:
            pass # there was no description tag

        #TODO: parameters, variables, handlers
        try:
            for p in root.getElementsByTagName("parameter"):
                self.parameters.append(p)
        except:
            pass # no parameters

        try:
            for v in root.getElementsByTagName("variable"):
                self.variables.append(v)
        except:
            pass # no variables

        try:
            for h in root.getElementsByTagName("handler"):
                self.handlers.append(h)
        except:
            pass
                

    def save(self):
        if self.name == "":
            return 
        if self.dir == "":
            self.dir = re.sub(r"\W","_",self.name)

        try:
            os.makedirs(BASE_DIR + os.sep + self.simulation.dir + os.sep + self.dir)
        except:
            pass

        f = open(BASE_DIR + os.sep + self.simulation.dir + os.sep +
                self.dir + os.sep + "federate.xml")
        f.write(self.as_xml())
        f.close()

    def as_xml(self):
        return """<?xml version="1.0"?>
        <federate system=%s name=%s>
        <description>%s</description>
        <parameters></parameters>
        <variables></variables>
        <handlers></handlers>""" % (saxutils.quoteattr(self.system),
                saxutils.quoteattr(self.name),
                saxutils.escape(self.description))

class Parameter:
    def __init__(self,name,type):
        self.name = name
        self.type = type
        
class OptimusDrawWindow(wxScrolledWindow):
    def __init__(self, parent, id = -1,size=wxDefaultSize):
        self.canvas = None
        (self.width,self.height) = size
        wxScrolledWindow.__init__(self, parent, id, wxPoint(0,0),
                wxDefaultSize,
                wxSUNKEN_BORDER)
        self.SetScrollbars(20,20, self.width/20, self.height/20)
        self.SetBackgroundColour("WHITE")

        self.buffer = wxEmptyBitmap(self.width,self.height)
        dc = wxBufferedDC(None, self.buffer)
        dc.SetBackground(wxBrush(self.GetBackgroundColour()))
        dc.Clear()
        self.DoDrawing(dc)
        EVT_PAINT(self,self.OnPaint)
        
    def OnPaint(self, event):
        dc = wxBufferedPaintDC(self, self.buffer)
        
    def DoDrawing(self, dc):
        dc.BeginDrawing()
        dc.SetBackground(wxBrush("white"))
        dc.Clear()

        if self.canvas != None:
            img = self.canvas.as_image()
            (w,h) = img.size
            image = wxEmptyImage(w,h)
            image.SetData(img.convert("RGB").tostring())
            dc.DrawBitmap(image.ConvertToBitmap(),0,0)

        dc.EndDrawing()

    def update(self):
        dc = wxBufferedPaintDC(self, self.buffer)
        self.DoDrawing(dc)

ID_Start = wxNewId()
ID_Stop = wxNewId()
ID_Timer = wxNewId()
TICK_MILLISECONDS = 10

class CanvasPanel(wxPanel):
    """ the panel which contains the canvas and run control buttons """
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        self.optimus = get_optimus()
        box = wxBoxSizer(wxVERTICAL)
        buttonbox = wxBoxSizer(wxHORIZONTAL)

        self.dw = OptimusDrawWindow(self,-1,(800,600))

        self.dw.canvas = self.MakeNewCanvas()
        self.dw.canvas.layers = self.MakeLayers()
        self.dw.canvas.default_grid()
        self.dw.update()
        
        ss = wxNewId()
        step = wxNewId()
        reset = wxNewId()
        runnsteps = wxNewId()
        console = wxNewId()
        
        self.ssbutton = wxButton(self,ss,"start")
        self.stepbutton = wxButton(self,step,"step")
        self.resetbutton = wxButton(self,reset,"reset")
        self.runnsteps = wxButton(self,runnsteps,"run N steps")
        self.consolebutton = wxButton(self,console,"console")

        EVT_BUTTON(self,ss,self.ssbutton_clicked)
        EVT_BUTTON(self,step,self.stepbutton_clicked)
        EVT_BUTTON(self,reset,self.resetbutton_clicked)
        EVT_BUTTON(self,runnsteps,self.runnsteps_clicked)
        EVT_BUTTON(self,console,self.ShowConsole)

        box.Add(self.dw,1,wxEXPAND)
        box.Add(buttonbox,0,wxEXPAND)

        buttonbox.Add(self.runnsteps)
        buttonbox.Add(self.ssbutton)
        buttonbox.Add(self.stepbutton)
        buttonbox.Add(self.resetbutton)
        buttonbox.Add(self.consolebutton)

        self.runnsteps.Disable()
        self.ssbutton.Disable()
        self.stepbutton.Disable()
        self.resetbutton.Disable()
        
        self.SetSizer(box)
        self.running = 0
        self.counting = false
        self.counter = 0
        self.n = 100

        self.timer = wxTimer(self,ID_Timer)
        EVT_TIMER(self,  ID_Timer, self.OnTimer)
        
    def ShowConsole(self,event):
        console = ConsoleFrame()
        console.Show(true)

    def MakeNewCanvas(self):
        return TileEngineCanvas(400,300,800,600)

    def MakeLayers(self):
        c = self.dw.canvas
#        bg = ImageLayer(c,400,300,"bg.png",256,0,0)
        return []

    def simulation_loaded(self):
        self.runnsteps.Enable(true)
        self.ssbutton.Enable(true)
        self.stepbutton.Enable(true)
        self.resetbutton.Enable(true)

    def runnsteps_clicked(self,event):
        if self.running:
            self.running = 0
            self.timer.Stop()
        else:
            self.running = 1
            self.counting = true
            self.counter = 0
            dlg = wxTextEntryDialog(self, 'run for how many steps?')
            dlg.SetValue(str(self.n))
            if dlg.ShowModal() == wxID_OK:
                self.n = int(dlg.GetValue())
                self.timer.Start(TICK_MILLISECONDS)
            dlg.Destroy()

            
        if self.running:
            self.ssbutton.SetLabel("stop")
        else:
            self.ssbutton.SetLabel("start")

    def ssbutton_clicked(self, event):
        if self.running:
            self.running = 0
            self.timer.Stop()
        else:
            self.running = 1
            self.timer.Start(TICK_MILLISECONDS)

        
        if self.running:
            self.ssbutton.SetLabel("stop")
        else:
            self.ssbutton.SetLabel("start")

    def stepbutton_clicked(self, event):
        pass

    def resetbutton_clicked(self, event):
        pass

    def stop_timer(self):
        self.timer.Stop()
        self.running = 0
        self.ssbutton.SetLabel("start")
        self.runnsteps.SetLabel("run N steps")

    def OnTimer(self,event):
        if self.counting:
            self.counter += 1

        if self.counter > self.n and self.counting:
            self.stop_timer()
            return
        else:
            self.optimus.debug("---- tick ----")
            if self.counting:
                self.runnsteps.SetLabel("run %d steps" \
                        % (self.n - self.counter))


class ParametersPanel(wxPanel):
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        box = wxBoxSizer(wxVERTICAL)
        self.list_id = wxNewId()
        self.params = wxListCtrl(self,self.list_id,style=wxLC_REPORT|wxSUNKEN_BORDER)
        box.Add(self.params,1,wxEXPAND)
        buttonbox = wxBoxSizer(wxHORIZONTAL)
        self.padd = wxButton(self,18,"Add Parameter")
        self.psave = wxButton(self,20,"Save")
        buttonbox.Add(self.padd)
        buttonbox.Add(self.psave)
        self.psave.Disable()
        box.Add(buttonbox,0,wxEXPAND)
        self.SetSizer(box)
        EVT_LIST_ITEM_SELECTED(self,self.list_id,self.on_parameter_selected)
        self.parameters = []

    def load_parameters(self,parameters):
        self.parameters = parameters
        while self.params.GetColumnCount():
            self.params.DeleteColumn(0)
        self.params.InsertColumn(0,"Name")
        self.params.InsertColumn(1,"Type")
        self.params.SetColumnWidth(0,200)
        i = 0
        for p in self.parameters:
            self.params.InsertStringItem(i,p.name)
            self.params.InsertStringItem(i,p.type)
            i += 1
        self.padd.Enable(true)

    def on_parameter_selected(self,event):
        self.psave.Enable(true)
        

class VariablesPanel(wxPanel):
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        box = wxBoxSizer(wxVERTICAL)
        variables = wxListCtrl(self,-1)
        box.Add(variables,1,wxEXPAND)
        buttonbox = wxBoxSizer(wxHORIZONTAL)
        vadd = wxButton(self,18,"Add Variable")
        vsave = wxButton(self,20,"Save")
        buttonbox.Add(vadd)
        buttonbox.Add(vsave)
        vsave.Disable()
        box.Add(buttonbox,0,wxEXPAND)
        self.SetSizer(box)

class EventHandlersPanel(wxPanel):
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        box = wxBoxSizer(wxVERTICAL)
        handlers = wxListCtrl(self,-1)
        box.Add(handlers,1,wxEXPAND)
        buttonbox = wxBoxSizer(wxHORIZONTAL)
        eadd = wxButton(self,18,"Add Event Handler")
        esave = wxButton(self,20,"Save")
        buttonbox.Add(eadd)
        buttonbox.Add(esave)
        esave.Disable()
        box.Add(buttonbox,0,wxEXPAND)
        self.SetSizer(box)
        
    
class FederatesPanel(wxPanel):
    """ panel containing federate editing stuff"""
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        box = wxBoxSizer(wxVERTICAL)
        self.listid = wxNewId()
        self.federates_list = wxListCtrl(self,self.listid,style=wxLC_REPORT|wxSUNKEN_BORDER)
        
        box.Add(self.federates_list,2,wxEXPAND)
        fbuttonbox = wxBoxSizer(wxHORIZONTAL)
        self.fadd = wxButton(self,15,"Add")
        self.fdel = wxButton(self,16,"Delete")
        self.fedit = wxButton(self,17,"Edit")
        fbuttonbox.Add(self.fadd)
        fbuttonbox.Add(self.fdel)
        fbuttonbox.Add(self.fedit)
        
        self.fadd.Disable()
        self.fdel.Disable()
        self.fedit.Disable()
        
        box.Add(fbuttonbox,0,wxEXPAND)
        nb = wxNotebook(self,-1)
        self.ppanel = ParametersPanel(nb,-1)
        self.vpanel = VariablesPanel(nb,-1)
        self.epanel = EventHandlersPanel(nb,-1)
        nb.AddPage(self.ppanel,"parameters")
        nb.AddPage(self.vpanel,"variables")
        nb.AddPage(self.epanel,"event handlers")

        box.Add(nb,3,wxEXPAND)
        self.SetSizer(box)

        EVT_LIST_ITEM_SELECTED(self,self.listid,self.on_federate_selected)
        EVT_LEFT_DCLICK(self,self.on_double_click)
        self.selected_federate = None

    def load_federates(self,federates):
        self.federates = federates
        while self.federates_list.GetColumnCount():
            self.federates_list.DeleteColumn(0)
        self.federates_list.InsertColumn(0,"Federate")
        self.federates_list.SetColumnWidth(0,200)
        i = 0
        for f in self.federates:
            self.federates_list.InsertStringItem(i,f.name)
            i += 1
        self.fadd.Enable(true)

    def on_federate_selected(self,event):
        self.fdel.Enable(true)
        self.fedit.Enable(true)
        self.selected_federate = self.federates[event.m_itemIndex]
        p1 = Parameter("foo","bar")
        p2 = Parameter("oof","rab")
        self.ppanel.load_parameters([p1,p2])

    def on_double_click(self,event):
        print "double clicked"
        
        
class SimulationsPanel(wxPanel):
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        self.optimus = get_optimus()
        box = wxBoxSizer(wxVERTICAL)
        
        self.listid = wxNewId()
        self.list = wxListCtrl(self,self.listid,
                style=wxLC_REPORT|wxSUNKEN_BORDER)

        EVT_LIST_ITEM_SELECTED(self,self.listid,self.on_simulation_selected)
        EVT_LEFT_DCLICK(self.list, self.on_double_click)

        box.Add(self.list,1,wxEXPAND)
        buttonbox = wxBoxSizer(wxHORIZONTAL)

        add = wxNewId()
        load = wxNewId()

        self.add  = wxButton(self,add,"Add")
        self.rem  = wxButton(self,22,"Delete")
        self.edit = wxButton(self,23,"Edit")
        self.load = wxButton(self,load,"Load")

        EVT_BUTTON(self,add,self.on_add_simulation_clicked)
        EVT_BUTTON(self,load,self.on_load_clicked)

        buttonbox.Add(self.add)
        buttonbox.Add(self.rem)
        buttonbox.Add(self.edit)
        buttonbox.Add(self.load)

        self.rem.Disable()
        self.edit.Disable()
        self.load.Disable()

        box.Add(buttonbox,0,wxEXPAND)
        self.SetSizer(box)
        self.populate_list()

    def populate_list(self):
        self.load_simulations()
        # clear the list
        while self.list.GetColumnCount() :
            self.list.DeleteColumn(0)
            
        self.list.InsertColumn(0,"Simulation")
        self.list.SetColumnWidth(0,200)
        i = 0
        for s in self.simulations:
            self.list.InsertStringItem(i,s.name)
            i += 1

    def load_simulations(self):
        self.simulations = []
        for sim in os.listdir('simulations'):
            if os.path.isfile('simulations' + os.sep + sim + os.sep +
                    "simulation.xml") and sim != "CVS":
                s = Simulation()
                s.load_from_file(sim)
                self.simulations.append(s)

    def on_simulation_selected(self,event):
        self.rem.Enable(true)
        self.edit.Enable(true)
        self.load.Enable(true)
        self.selected_simulation = self.simulations[event.m_itemIndex]
        
    def on_double_click(self,event):
        print "double clicked"

    def on_add_simulation_clicked(self,event):
        dialog = AddSimulationDialog(self,-1)
        val = dialog.ShowModal()
        if val == wxID_OK:
            name = dialog.get_name()
            description = dialog.get_description()
            s = Simulation(name = name, description=description)
            s.save()

    def on_load_clicked(self,event):
        self.optimus.load_simulation(self.selected_simulation)



class AddSimulationDialog(wxDialog):
    def __init__(self,parent,id):
        wxDialog.__init__(self,parent,-1,"Add New Simulation", size=wxSize(350, 200), style=wxCAPTION)
        box = wxBoxSizer(wxVERTICAL)
        nbox = wxBoxSizer(wxHORIZONTAL)
        l1 = wxStaticText(self,-1,"Simulation Name: ")
        self.name = wxTextCtrl(self, -1, "", size=(80,-1))
        nbox.Add(l1,0,wxEXPAND)
        nbox.Add(self.name,1,wxEXPAND)
        box.Add(nbox,0,wxEXPAND)

        dbox = wxBoxSizer(wxHORIZONTAL)
        l2 = wxStaticText(self, -1, "Description: ")
        self.description = wxTextCtrl(self, -1, "", size=(100,200),style=wxTE_MULTILINE)
        dbox.Add(l2,0,wxEXPAND)
        dbox.Add(self.description,1,wxEXPAND)
        box.Add(dbox,1,wxEXPAND)

        buttonbox = wxBoxSizer(wxHORIZONTAL)
        btn = wxButton(self, wxID_OK, " OK ")
        btn.SetDefault()
        buttonbox.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        btn = wxButton(self, wxID_CANCEL, " Cancel ")
        buttonbox.Add(btn, 0, wxALIGN_CENTRE|wxALL, 5)

        box.Add(buttonbox,0,wxEXPAND)

        self.SetSizer(box)

    def get_name(self):
        return self.name.GetValue()

    def get_description(self):
        return self.description.GetValue()
    
        
class ScenariosPanel(wxPanel):
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        l1 = wxStaticText(self,-1,"not implemented yet")

class RightPanel(wxPanel):
    def __init__(self,parent,id):
        wxPanel.__init__(self,parent,-1)
        box = wxBoxSizer(wxVERTICAL)
        nb = wxNotebook(self,-1)
        self.simpanel = SimulationsPanel(nb,-1)
        self.fedpanel = FederatesPanel(nb,-1)
        self.scepanel = ScenariosPanel(nb,-1)

        nb.AddPage(self.simpanel,"Simulations")
        nb.AddPage(self.fedpanel,"Federates")
        nb.AddPage(self.scepanel,"Scenarios")
        box.Add(nb,1,wxEXPAND)
        self.SetSizer(box)

class ConsoleFrame(wxFrame):
    def __init__(self):
        wxFrame.__init__(self,NULL,-1,"Optimus Console",
                wxDefaultPosition,
                size=(400,500),
                style=wxDEFAULT_FRAME_STYLE)
        self.optimus = get_optimus()
        self.log = self.optimus.log
        box = wxBoxSizer(wxVERTICAL)
        self.text = wxTextCtrl(self,-1,"",size=(200,300),
                style=wxTE_MULTILINE)
        box.Add(self.text,1,wxEXPAND)
        buttonbox = wxBoxSizer(wxHORIZONTAL)
        close = wxNewId()
        clear = wxNewId()
        self.clear_button = wxButton(self,clear,"Clear")
        self.close_button = wxButton(self,close,"Close")
        EVT_BUTTON(self,close,self.CloseWindow)
        EVT_BUTTON(self,clear,self.Clear)
        
        errors = wxNewId()
        warnings = wxNewId()
        debugs = wxNewId()
        
        self.errors_cb = wxCheckBox(self,errors,"errors")
        self.warnings_cb = wxCheckBox(self,warnings,"warnings")
        self.debug_cb = wxCheckBox(self,debugs,"debug")
        
        if self.log.errors:
            self.errors_cb.SetValue(true)
        if self.log.warnings:
            self.warnings_cb.SetValue(true)
        if self.log.debugs:
            self.debug_cb.SetValue(true)

        EVT_CHECKBOX(self,errors,self.errors_checked)
        EVT_CHECKBOX(self,warnings,self.warnings_checked)
        EVT_CHECKBOX(self,debugs,self.debugs_checked)
        
        buttonbox.Add(self.clear_button)
        buttonbox.Add(self.errors_cb)
        buttonbox.Add(self.warnings_cb)
        buttonbox.Add(self.debug_cb)
        buttonbox.Add(self.close_button)
        box.Add(buttonbox,0,wxEXPAND)

        self.load_text()

        self.SetSizer(box)

    def load_text(self):
        self.text.Clear()
        f = wxFont(-1, wxROMAN, 0, 0, true)

        colors = {
        "error" : wxTextAttr("RED","WHITE",f),
        "warning" : wxTextAttr("ORANGE","WHITE",f),
        "debug" : wxTextAttr("BLACK","WHITE",f)
        }
        start_point = self.text.GetInsertionPoint()
        for (mtype,message) in self.log.messages:
            if (mtype == "error" and self.log.errors) \
                    or (mtype == "warning" and self.log.warnings) \
                    or (mtype == "debug" and self.log.debugs):
            
                self.text.AppendText(mtype + ": " + message + "\n")
                end_point = self.text.GetInsertionPoint()
                self.text.SetStyle(start_point,end_point,colors[mtype])
                start_point = end_point

    def CloseWindow(self,event):
        self.Close()

    def Clear(self,event):
        self.log.clear()
        self.load_text()

    def errors_checked(self,event):
        self.log.errors = event.Checked()
        self.load_text()

    def warnings_checked(self,event):
        self.log.warnings = event.Checked()
        self.load_text()

    def debugs_checked(self,event):
        self.log.debugs = event.Checked()
        self.load_text()


class OptimusFrame(wxFrame):
    def __init__(self):
        wxFrame.__init__(self,NULL,-1,"Optimus",
                wxDefaultPosition,
                size=(800,600),
                style=wxDEFAULT_FRAME_STYLE)
        self.CreateStatusBar()
        self.setup_menubar()
        self.mainbox = wxBoxSizer(wxHORIZONTAL)
        self.cp = CanvasPanel(self,-1)
        self.rp = RightPanel(self,-1)
        self.mainbox.Add(self.cp,5,wxEXPAND)
        self.mainbox.Add(self.rp,4,wxEXPAND)
        self.SetSizer(self.mainbox)

    def setup_menubar(self):
        self.menubar = wxMenuBar()
        filemenu = wxMenu()
        filemenu.Append(102,"Exit","Exit optimus")
        EVT_MENU(self,102,self.CloseWindow)
        self.menubar.Append(filemenu,"File")
        self.SetMenuBar(self.menubar)

    def CloseWindow(self,event):
        self.Close()

class OptimusApp(wxApp):
    def OnInit(self):
        self.frame = OptimusFrame()
        self.frame.Show(1)
        self.SetTopWindow(self.frame)
        return true

OPTIMUS = None
def register_optimus(opt):
    global OPTIMUS
    OPTIMUS = opt

def get_optimus():
    global OPTIMUS
    return OPTIMUS

class Optimus:
    def __init__(self):
        register_optimus(self)
        self.log = Log()
        self.app = OptimusApp()

        self.debug("created new Optimus object")
        self.warning("here's a warning")
        self.error("AHHH!! Chaos and Doom!!!")
        
        self.app.MainLoop()

    def load_simulation(self,simulation):
        self.loaded_simulation = simulation
        self.app.frame.rp.fedpanel.load_federates(simulation.federates)
        self.app.frame.cp.simulation_loaded()


    def debug(self,message):
        self.log.debug(message)

    def warning(self,message):
        self.log.warning(message)

    def error(self,message):
        self.log.error(message)

        


if __name__ == "__main__":
    optimus = Optimus()



