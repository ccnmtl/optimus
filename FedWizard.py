#!/usr/bin/python

import pygtk
import gtk
import gtk.glade
import gobject
import os
from xml.dom.minidom import Document, parseString
from xml.sax import saxutils
from FederateXML import Federate
from SimulationXML import Simulation

gladefile = "fedwizard.glade"
base_dir = "simulations"

class FedWizard:
    def __init__(self):
        windowname = "fedwizardmain"
        self.wTree = gtk.glade.XML(gladefile,windowname)
        dic = {
        'on_fedwizardmain_destroy' : (gtk.mainquit),
        'on_add_clicked' : self.add_clicked,
        'on_edit_clicked' : self.edit_clicked,
        'on_delete_clicked' : self.delete_clicked,
        }
        self.wTree.signal_autoconnect(dic)
        self.treestore = gtk.TreeStore(str,str,gobject.TYPE_PYOBJECT)
        self.populate_simulations_tree()
        self.treeview = self.wTree.get_widget("simulations_view")
        self.treeview.set_model(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn('Column 0')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.treeview.show()
        
    def load_simulations(self):
        self.simulations = []
        for sim in os.listdir('simulations'):
            if os.path.isfile('simulations' + os.sep + sim + os.sep + "simulation.xml") and sim != 'CVS':
                self.simulations.append(Sim(sim))

    def populate_simulations_tree(self):
        self.treestore.clear()
        self.load_simulations()
        for s in self.simulations:
            print "Simulation: %s" % s.simulation.name
            piter = self.treestore.append(None, [s.simulation.name,'simulation',s])
            for fed in s.federates:
                self.treestore.append(piter, [fed.federate.name, 'federate', fed])
          
    def add_clicked(self,widget):
        selection = self.treeview.get_selection()
        model,iter = selection.get_selected()
        path = model.get_path(iter)
        sim = model[path[0]][0]
        AddFederate(self,sim)

    def edit_clicked(self,widget):
        selection = self.treeview.get_selection()
        model,iter = selection.get_selected()
        data = model.get_value(iter,0)
        type = model.get_value(iter,1)
        obj  = model.get_value(iter,2)
        if type == 'federate':
            f = EditFederate(self,obj,obj.sim)

    def delete_clicked(self,widget):
        selection = self.treeview.get_selection()
        model,iter = selection.get_selected()
        data = model.get_value(iter,0)
        type = model.get_value(iter,1)
        obj  = model.get_value(iter,2)
        if type == 'federate':
            sim = obj.sim
            sim.delete_federate(obj.federate.system)
            self.populate_simulations_tree()
        

class AddFederate:
    def __init__(self,parent,sim):
        self.parent = parent
        self.sim = Sim(sim)
        self.wTree = gtk.glade.XML(gladefile,"addfederate")
        dic = {
        'on_cancel_clicked' : self.cancel,
        'on_ok_clicked' : self.ok,
        }
        self.wTree.signal_autoconnect(dic)
        self.window = self.wTree.get_widget("addfederate")
        self.window.run()
        
    def cancel(self,widget):
        self.close()

    def ok(self,widget):
        name = self.wTree.get_widget("name").get_text()
        system = self.wTree.get_widget("system").get_text()
        xml = """<?xml version="1.0"?>
        <federate name="%s" system="%s">
        <description></description>
        <attributes/>
        <handlers/>
        </federate>""" % (name,system)
        try:
            os.makedirs(base_dir + os.sep + self.sim.dir + os.sep + name)
        except: 
            pass
        open(base_dir + os.sep + self.sim.dir + os.sep + name + os.sep + \
                "federate.xml","w").write(xml)
        self.sim.simulation.add_federate(system=system,file=system + \
                os.sep + "federate.xml")
        self.sim.save()
        self.parent.populate_simulations_tree()
        self.close()
        fed = Fed(self.sim,system)
        f = EditFederate(self.parent,fed,self.sim)
        
    def close(self):
        self.window.hide()

class EditFederate:
    def __init__(self,parent,federate,sim):
        self.parent = parent
        self.federate = federate
        self.sim = sim
        if self.federate == None:
            self.federate = Fed(self.sim,None)
        self.wTree = gtk.glade.XML(gladefile,"editfederate")
        dic = {
        'on_cancel_clicked' : self.cancel,
        'on_ok_clicked' : self.ok,
        'on_attributes_view_cursor_changed' : self.attribute_selected,
        'on_handlers_view_cursor_changed' : self.handler_selected,
        'on_bindings_view_cursor_changed' : self.binding_selected,
        'on_add_attribute_clicked' : self.add_attribute,
        'on_edit_attribute_clicked' : self.edit_attribute,
        'on_delete_attribute_clicked' : self.delete_attribute,
        'on_add_handler_clicked' : self.add_handler,
        'on_edit_handler_clicked' : self.edit_handler,
        'on_delete_handler_clicked' : self.delete_handler,
        'on_add_binding_clicked' : self.add_binding,
        'on_edit_binding_clicked' : self.edit_binding,
        'on_delete_binding_clicked' : self.delete_binding,
        }
        self.wTree.signal_autoconnect(dic)
        
        self.wTree.get_widget("name").insert_text(str(self.federate.federate.name))
        self.wTree.get_widget("system").insert_text(str(self.federate.federate.system))

        self.description_buffer = gtk.TextBuffer()
        self.wTree.get_widget("description").set_buffer(self.description_buffer)
        self.description_buffer.set_text(str(self.federate.federate.description))

        # attributes

        self.attributes_view = self.wTree.get_widget('attributes_view')
        self.attributes_store = gtk.ListStore(str,str,str,str,str,str,str,int)
        self.attributes_view.set_model(self.attributes_store)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("name",renderer,text=0)
        self.attributes_view.append_column(column)
        column = gtk.TreeViewColumn("varname",renderer,text=1)
        self.attributes_view.append_column(column)
        column = gtk.TreeViewColumn("type",renderer,text=2)
        self.attributes_view.append_column(column)
        column = gtk.TreeViewColumn("label",renderer,text=3)
        self.attributes_view.append_column(column)
        column = gtk.TreeViewColumn("min",renderer,text=4)
        self.attributes_view.append_column(column)
        column = gtk.TreeViewColumn("max",renderer,text=5)
        self.attributes_view.append_column(column)
        column = gtk.TreeViewColumn("default",renderer,text=6)
        self.attributes_view.append_column(column)

        self.attributes_view.show()
        self.load_attributes()

        # handlers

        self.handlers_view = self.wTree.get_widget('handlers_view')
        self.handlers_store = gtk.ListStore(str,str,int)
        self.handlers_view.set_model(self.handlers_store)
        column = gtk.TreeViewColumn("event",renderer,text=0)
        self.handlers_view.append_column(column)

        self.handlers_view.show()
        self.load_handlers()

        self.handler_code_buffer = gtk.TextBuffer()
        self.wTree.get_widget("handler_code").set_buffer(self.handler_code_buffer)

        # bindings

        self.bindings_view = self.wTree.get_widget("bindings_view")
        self.bindings_store = gtk.ListStore(str,str,str,str,int)
        self.bindings_view.set_model(self.bindings_store)
        column = gtk.TreeViewColumn("localname",renderer,text=0)
        self.bindings_view.append_column(column)
        column = gtk.TreeViewColumn("system",renderer,text=1)
        self.bindings_view.append_column(column)
        column = gtk.TreeViewColumn("variable",renderer,text=2)
        self.bindings_view.append_column(column)
        column = gtk.TreeViewColumn("default",renderer,text=3)
        self.bindings_view.append_column(column)
        self.bindings_view.show()
        self.load_bindings()
        

        self.window = self.wTree.get_widget("editfederate")
        self.window.run()

    def load_attributes(self):
        self.attributes_store.clear()
        idx = 0
        for a in self.federate.federate.attributes[0].attributes:
            print a.name
            self.attributes_store.append([a.name, a.varname,
            a.type, a.label, a.min, a.max, a.default, idx])
            idx += 1
            
    def load_handlers(self):
        self.handlers_store.clear()
        idx = 0
        for h in self.federate.handlers:
            self.handlers_store.append([h.type, h.code,idx])
            idx += 1

    def load_bindings(self):
        self.bindings_store.clear()
        idx = 0
        for b in self.federate.bindings:
            self.bindings_store.append([b.localname, b.system,
            b.variable, b.default,idx])
            idx += 1

    def attribute_selected(self,widget):
        selection = self.attributes_view.get_selection()
        model,selected = selection.get_selected()
        path = model.get_path(selected)
        name = self.attributes_store[path[0]][0]
        varname = self.attributes_store[path[0]][1]
        type = self.attributes_store[path[0]][2]
        label = self.attributes_store[path[0]][3]
        min = self.attributes_store[path[0]][4]
        max = self.attributes_store[path[0]][5]
        default = self.attributes_store[path[0]][6]

        self.wTree.get_widget("attribute_name").set_text(name)
        self.wTree.get_widget("attribute_varname").set_text(varname)
        self.wTree.get_widget("attribute_type").set_text(type)
        self.wTree.get_widget("attribute_label").set_text(label)
        self.wTree.get_widget("attribute_min").set_text(min)
        self.wTree.get_widget("attribute_max").set_text(max)
        self.wTree.get_widget("attribute_default").set_text(default)
        

    def handler_selected(self,widget):
        selection = self.handlers_view.get_selection()
        model, selected = selection.get_selected()
        path = model.get_path(selected)
        event = self.handlers_store[path[0]][0]
        code = self.handlers_store[path[0]][1]
        self.wTree.get_widget("handler_event").set_text(event)
        self.handler_code_buffer.set_text(str(code))

    def binding_selected(self,widget):
        selection = self.bindings_view.get_selection()
        model, selected = selection.get_selected()
        path = model.get_path(selected)
        localname = self.bindings_store[path[0]][0]
        system = self.bindings_store[path[0]][1]
        variable = self.bindings_store[path[0]][2]
        default = self.bindings_store[path[0]][3]
        self.wTree.get_widget("binding_localname").set_text(localname)
        self.wTree.get_widget("binding_variable").set_text(variable)
        self.wTree.get_widget("binding_system").set_text(system)
        self.wTree.get_widget("binding_default").set_text(default)

    def add_attribute(self,widget):
        name = self.wTree.get_widget('attribute_name').get_text()
        varname = self.wTree.get_widget("attribute_varname").get_text()
        type = self.wTree.get_widget("attribute_type").get_text()
        label = self.wTree.get_widget("attribute_label").get_text()
        min = self.wTree.get_widget("attribute_min").get_text()
        max = self.wTree.get_widget("attribute_max").get_text()
        default = self.wTree.get_widget("attribute_default").get_text()

        self.federate.federate.add_attribute(name,varname,type,label,min,max,default)
        self.load_attributes()
        

    def edit_attribute(self,widget):
        name = self.wTree.get_widget('attribute_name').get_text()
        varname = self.wTree.get_widget("attribute_varname").get_text()
        type = self.wTree.get_widget("attribute_type").get_text()
        label = self.wTree.get_widget("attribute_label").get_text()
        min = self.wTree.get_widget("attribute_min").get_text()
        max = self.wTree.get_widget("attribute_max").get_text()
        default = self.wTree.get_widget("attribute_default").get_text()

        selection = self.attributes_view.get_selection()
        model,selected = selection.get_selected()
        path = model.get_path(selected)
        idx = self.attributes_store[path[0]][7]

        self.federate.federate.attributes[0].attributes[idx].name = name
        self.federate.federate.attributes[0].attributes[idx].varname = varname
        self.federate.federate.attributes[0].attributes[idx].type = type
        self.federate.federate.attributes[0].attributes[idx].label = label
        self.federate.federate.attributes[0].attributes[idx].min = min
        self.federate.federate.attributes[0].attributes[idx].max = max
        self.federate.federate.attributes[0].attributes[idx].default = default

        self.load_attributes()
        selection.select_path(path)

    def delete_attribute(self,widget):
        selection = self.attributes_view.get_selection()
        model,selected = selection.get_selected()
        path = model.get_path(selected)
        idx = self.attributes_store[path[0]][7]
        del self.federate.federate.attributes[0].atributes[idx]
        self.load_attributes()
        
        
    def add_handler(self,widget):
        event = self.wTree.get_widget("handler_event").get_text()
        sob,eob = self.handler_code_buffer.get_bounds()
        code = self.handler_code_buffer.get_text(sob,eob) 
        self.federate.federate.add_handler(event,code)
        self.load_handlers()

    def edit_handler(self,widget):

        event = self.wTree.get_widget("handler_event").get_text()
        sob,eob = self.handler_code_buffer.get_bounds()
        code = self.handler_code_buffer.get_text(sob,eob)
        
        selection = self.handlers_view.get_selection()
        model,selected = selection.get_selected()
        path = model.get_path(selected)
        idx = self.handlers_store[path[0]][2]
        self.federate.federate.handlers[0].events[idx].type = event
        self.federate.federate.handlers[0].events[idx].code = code
        self.load_handlers()
        selection.select_path(path)

    def delete_handler(self,widget):
        selection = self.handlers_view.get_selection()
        model,selected = selection.get_selected()
        path = model.get_path(selected)
        idx = self.handlers_store[path[0]][2]
        del self.federate.handlers[0].events[idx]
        self.load_handlers()

        
    def add_binding(self,widget):
        localname = self.wTree.get_widget("binding_localname").get_text()
        system    = self.wTree.get_widget("binding_system").get_text()
        variable  = self.wTree.get_widget("binding_variable").get_text()
        default   = self.wTree.get_widget("binding_default").get_text()
        
        self.federate.add_binding(localname,system,variable,default)
        self.load_bindings()

    def edit_binding(self,widget):
        localname = self.wTree.get_widget("binding_localname").get_text()
        system    = self.wTree.get_widget("binding_system").get_text()
        variable  = self.wTree.get_widget("binding_variable").get_text()
        default   = self.wTree.get_widget("binding_default").get_text()

        selection = self.bindings_view.get_selection()
        model,selected = selection.get_selected()
        path = model.get_path(selected)
        idx = self.bindings_store[path[0]][4]
        self.federate.bindings[idx]['localname'] = localname
        self.federate.bindings[idx]['system']    = system
        self.federate.bindings[idx]['variable']  = variable
        self.federate.bindings[idx]['default']   = default
        self.load_bindings()
        selection.select_path(path)

    def delete_binding(self,widget):
        selection = self.bindings_view.get_selection()
        model,selected = selection.get_selected()
        path = model.get_path(selected)
        idx = self.bindings_store[path[0]][4]
        del self.federate.federate.bindings[0].variables[idx]
        self.load_bindings()
        
        

    def cancel(self,widget):
        self.close()

    def ok(self,widget):
        self.federate.save()
        self.close()
        
    def close(self):
        self.window.hide()


class Fed:
    def __init__(self,sim,dir):
        self.sim = sim
        self.dir = dir
        self.file = "federate.xml"

        if self.dir != None:
            xml = open(base_dir + os.sep + self.sim.dir + os.sep + self.dir + \
                    os.sep + "federate.xml", "r").read()
            self.federate = Federate.fromXml(xml)
        else:
            self.federate = Federate(name="",system="",description="")
            
        self.attributes = []
        self.handlers = []
        self.bindings = []
        if self.federate.attributes:
            self.attributes = self.federate.attributes[0].attributes
        if self.federate.handlers:
            self.handlers = self.federate.handlers[0].events
        if self.federate.bindings:
            self.bindings = self.federate.bindings[0].variables
        for h in self.handlers:
            h.code = open(base_dir + os.sep + self.sim.dir + os.sep + \
                    self.dir + os.sep + h.file, "r").read()
            
    def delete_self(self):
        # we won't actually delete the files yet. just to be on the safe
        # side.
        pass

    def save(self):
        xml = self.federate.toXml()
        if self.dir == None:
            self.dir = self.system
        open(base_dir + os.sep + self.sim.dir + os.sep + self.dir + \
                os.sep + self.file, "w").write(xml)
        for event in self.federate.handlers[0].events:
            code = event.code
            open(base_dir + os.sep + self.sim.dir + os.sep + \
                    self.dir + os.sep + event.file,"w").write(code)
            

class Sim:
    def __init__(self,dir):
        self.dir = dir
        self.federates = []
        xml = open(base_dir + os.sep + self.dir + os.sep + "simulation.xml","r").read()
        self.simulation = Simulation.fromXml(xml)
        for f in self.simulation.federates[0].federates:
            self.federates.append(Fed(self,f.system))

    def save(self):
        xml = self.simulation.toXml()
        open(base_dir + os.sep + self.dir + os.sep + "simulation.xml","w").write(xml)

    def delete_federate(self,federate_system):
        selected = 0
        idx = 0
        for f in self.simulation.federates[0].federates:
            if f.system == federate_system:
                selected = idx
            idx += 1
        del self.simulation.federates[0].federates[selected]
        self.save()

if __name__ == "__main__":
    f = FedWizard()
    gtk.mainloop()
