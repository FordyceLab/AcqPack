from IPython import display
from ipywidgets import widgets
import cv2

def video(core):
    import cv2
    cv2.namedWindow('Video')
    core.startContinuousSequenceAcquisition(1)
    while True:
        img = core.getLastImage()
        if core.getRemainingImageCount() > 0:
    #         img = core.popNextImage()
            img = core.getLastImage()
            cv2.imshow('Video', img)
            cv2.waitkey(0)
        else:
            print('No frame')
        if cv2.waitKey(20) >= 0:
            break
    core.stopSequenceAcquisition()
    cv2.destroyAllWindows()
    

def stage_control(XY, Z):
    # icons are from "font-awesome"
    x_minus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon = 'fa-arrow-left',
        width = '50px')
    def xminus(b):
        XY.r_xy(-xy_slider.value,0)
        display.clear_output()
        print(XY.where_xy())
    x_minus.on_click(xminus)

    x_plus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon = 'fa-arrow-right',
        width = '50px')
    def xplus(b):
        XY.r_xy(xy_slider.value,0)
        display.clear_output()
        print(XY.where_xy())
    x_plus.on_click(xplus)

    y_minus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary', 
        icon='fa-arrow-up',
        width = '50px')
    def yminus(b):
        XY.r_xy(0, -xy_slider.value)
        display.clear_output()
        print(XY.where_xy())
    y_minus.on_click(yminus)

    y_plus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon = 'fa-arrow-down',
        width = '50px')
    def yplus(b):
        XY.r_xy(0, xy_slider.value)
        display.clear_output()
        print(XY.where_xy())
    y_plus.on_click(yplus)


    xy_home = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon = 'fa-home',
        width = '50px')
    def xyhome(b):
        Z.home()
        XY.move_xy(0,0)
        display.clear_output()
        print(XY.where_xy())
    xy_home.on_click(xyhome)

    xy_slider = widgets.FloatSlider(description='[mm]', min=.05, max=10,step=.05, orientation='vertical', height='150px')
    def xystep(change):
        xy_step = change['new']
    xy_slider.observe(xystep, names='value')

    xy_cluster = widgets.HBox([ xy_slider, widgets.VBox([ widgets.HBox([x_minus,x_plus,xy_home]), widgets.HBox([y_minus, y_plus]) ]) ])


    z_minus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon = 'fa-arrow-up')
    def zminus(b):
        Z.move_relative(-z_slider.value)
        display.clear_output()
        print(Z.where())
    z_minus.on_click(zminus)

    z_plus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon = 'fa-arrow-down')
    def zplus(b):
        Z.move_relative(z_slider.value)
        display.clear_output()
        print(Z.where())
    z_plus.on_click(zplus)

    z_home = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon = 'fa-home',
        width = '50px')
    def zhome(b):
        Z.home()
        display.clear_output()
        print(Z.where())
    z_home.on_click(zhome)

    z_slider = widgets.FloatSlider(description='[mm]', min=.05, max=10,step=.05, orientation='vertical', height='150px')
    def zstep(change):
        z_step = change['new']
    z_slider.observe(zstep, names='value')

    z_cluster = widgets.VBox([ widgets.HBox([ z_slider, widgets.VBox([z_minus, z_plus]), z_home]) ])


    x_pos = widgets.Text(
        value='0',
        placeholder='Type something',
        description='X:',
        disabled=False,
        width='150px')
    def xpos(sender):
        xcurr,ycurr = XY.where_xy()
        XY.move_xy(sender.value,ycurr)
    x_pos.on_submit(xpos)

    y_pos = widgets.Text(
        value='0',
        placeholder='Type something',
        description='Y:',
        disabled=False,
        width='150px')
    def ypos(sender):
        xcurr,ycurr = XY.where_xy()
        XY.move_xy(xcurr, sender.value)
    y_pos.on_submit(ypos)

    z_pos = widgets.Text(
        value='0',
        placeholder='Type something',
        description='Z:',
        disabled=False,
        width='150px')
    def zpos(sender):
        Z.move(float(sender.value))
    z_pos.on_submit(zpos)

    line = widgets.Label(value="$---------------------------------------$",disabled=False)

    return widgets.VBox([ widgets.HBox([x_pos, y_pos, z_pos]), line, widgets.HBox([xy_cluster, z_cluster]) ])
